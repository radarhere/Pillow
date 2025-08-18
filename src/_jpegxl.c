#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdbool.h>
#include "libImaging/Imaging.h"

#include <jxl/codestream_header.h>
#include <jxl/decode.h>
#include <jxl/types.h>
#include <jxl/thread_parallel_runner.h>

void
_jxl_get_pixel_format(JxlPixelFormat *pf, const JxlBasicInfo *bi) {
    pf->num_channels = bi->num_color_channels + bi->num_extra_channels;

    if (bi->exponent_bits_per_sample > 0 || bi->alpha_exponent_bits > 0) {
        pf->data_type = JXL_TYPE_FLOAT;  // not yet supported
    } else if (bi->bits_per_sample > 8) {
        pf->data_type = JXL_TYPE_UINT16;  // not yet supported
    } else {
        pf->data_type = JXL_TYPE_UINT8;
    }

    // this *might* cause some issues on Big-Endian systems
    // would be great to test it
    pf->endianness = JXL_NATIVE_ENDIAN;
    pf->align = 0;
}

// TODO: floating point mode
char *
_jxl_get_mode(const JxlBasicInfo *bi) {
    // 16-bit single channel images are supported
    if (bi->bits_per_sample == 16 && bi->num_color_channels == 1 &&
        bi->alpha_bits == 0 && !bi->alpha_premultiplied) {
        return "I;16";
    }

    // PIL doesn't support high bit depth images
    // it will throw an exception but that's for your own good
    // you wouldn't want to see distorted image
    if (bi->bits_per_sample != 8) {
        return NULL;
    }

    // image has transparency
    if (bi->alpha_bits > 0) {
        if (bi->num_color_channels == 3) {
            if (bi->alpha_premultiplied) {
                return "RGBa";
            }
            return "RGBA";
        }
        if (bi->num_color_channels == 1) {
            if (bi->alpha_premultiplied) {
                return "La";
            }
            return "LA";
        }
    }

    // image has no transparency
    if (bi->num_color_channels == 3) {
        return "RGB";
    }
    if (bi->num_color_channels == 1) {
        return "L";
    }

    // could not recognize mode
    return NULL;
}

// Decoder type
typedef struct {
    PyObject_HEAD JxlDecoder *decoder;
    void *runner;

    uint8_t *jxl_data;        // input jxl bitstream
    Py_ssize_t jxl_data_len;  // length of input jxl bitstream

    uint8_t *outbuf;
    Py_ssize_t outbuf_len;

    uint8_t *jxl_icc;
    Py_ssize_t jxl_icc_len;
    uint8_t *jxl_exif;
    Py_ssize_t jxl_exif_len;
    uint8_t *jxl_xmp;
    Py_ssize_t jxl_xmp_len;

    JxlDecoderStatus status;
    JxlBasicInfo basic_info;
    JxlPixelFormat pixel_format;

    Py_ssize_t n_frames;

    char *mode;
} JpegXlDecoderObject;

static PyTypeObject JpegXlDecoder_Type;

void
_jxl_decoder_dealloc(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    if (decp->jxl_data) {
        free(decp->jxl_data);
        decp->jxl_data = NULL;
        decp->jxl_data_len = 0;
    }
    if (decp->outbuf) {
        free(decp->outbuf);
        decp->outbuf = NULL;
        decp->outbuf_len = 0;
    }
    if (decp->jxl_icc) {
        free(decp->jxl_icc);
        decp->jxl_icc = NULL;
        decp->jxl_icc_len = 0;
    }
    if (decp->jxl_exif) {
        free(decp->jxl_exif);
        decp->jxl_exif = NULL;
        decp->jxl_exif_len = 0;
    }
    if (decp->jxl_xmp) {
        free(decp->jxl_xmp);
        decp->jxl_xmp = NULL;
        decp->jxl_xmp_len = 0;
    }

    if (decp->decoder) {
        JxlDecoderDestroy(decp->decoder);
        decp->decoder = NULL;
    }
}

PyObject *
_jxl_decoder_rewind(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;
    JxlDecoderRewind(decp->decoder);
    Py_RETURN_NONE;
}

bool
_jxl_decoder_count_frames(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    decp->n_frames = 0;

    // count all JXL_DEC_NEED_IMAGE_OUT_BUFFER events
    while (decp->status != JXL_DEC_SUCCESS) {
        decp->status = JxlDecoderProcessInput(decp->decoder);

        if (decp->status == JXL_DEC_NEED_IMAGE_OUT_BUFFER) {
            if (JxlDecoderSkipCurrentFrame(decp->decoder) != JXL_DEC_SUCCESS) {
                return false;
            }
            decp->n_frames++;
        }
    }

    JxlDecoderRewind(decp->decoder);

    return true;
}

PyObject *
_jxl_decoder_new(PyObject *self, PyObject *args) {
    PyBytesObject *jxl_string;

    if (!PyArg_ParseTuple(args, "S", &jxl_string)) {
        return NULL;
    }

    const uint8_t *_tmp_jxl_data;
    Py_ssize_t _tmp_jxl_data_len;

    PyBytes_AsStringAndSize((PyObject *)jxl_string, (char **)&_tmp_jxl_data, &_tmp_jxl_data_len);

    JxlBasicInfo basic_info;
    uint8_t *jxl_icc;
    size_t jxl_icc_len;
    Py_ssize_t n_frames = 0;

    Py_ssize_t jxl_data_len = _tmp_jxl_data_len;
    uint8_t *jxl_data = malloc(jxl_data_len);
    memcpy(jxl_data, _tmp_jxl_data, jxl_data_len);

    JxlThreadParallelRunnerCreate(NULL, 4);
    JxlDecoder *decoder = JxlDecoderCreate(NULL);

    JxlDecoderStatus status = JxlDecoderSubscribeEvents(decoder, JXL_DEC_BASIC_INFO | JXL_DEC_COLOR_ENCODING | JXL_DEC_FRAME | JXL_DEC_FULL_IMAGE);

    status = JxlDecoderSetDecompressBoxes(decoder, JXL_TRUE);

    status = JxlDecoderSetInput(decoder, jxl_data, jxl_data_len);
    JxlDecoderCloseInput(decoder);

    // decode everything up to the first frame
    do {
        status = JxlDecoderProcessInput(decoder);
        printf("Status during first frame: %d\n", status);

        if (status == JXL_DEC_BASIC_INFO) {
            status = JxlDecoderGetBasicInfo(decoder, &basic_info);
        } else if (status == JXL_DEC_COLOR_ENCODING) {
            status = JxlDecoderGetICCProfileSize(
                decoder,
#if JPEGXL_MINOR_VERSION < 9
                NULL,
#endif
                JXL_COLOR_PROFILE_TARGET_DATA,
                &jxl_icc_len
            );

            jxl_icc = malloc(jxl_icc_len);
            status = JxlDecoderGetColorAsICCProfile(
                decoder,
#if JPEGXL_MINOR_VERSION < 9
                NULL,
#endif
                JXL_COLOR_PROFILE_TARGET_DATA,
                jxl_icc,
                jxl_icc_len
            );
        }
    } while (status != JXL_DEC_FRAME);

    if (basic_info.have_animation) {
        while (status != JXL_DEC_SUCCESS) {
            status = JxlDecoderProcessInput(decoder);

            if (status == JXL_DEC_NEED_IMAGE_OUT_BUFFER) {
                JxlDecoderSkipCurrentFrame(decoder);
                n_frames++;
            }
        }
        JxlDecoderRewind(decoder);
    }

    JxlFrameHeader fhdr = {};

    while (status != JXL_DEC_NEED_IMAGE_OUT_BUFFER) {
        status = JxlDecoderProcessInput(decoder);
        printf("Status: %d\n", status);

        if (status == JXL_DEC_SUCCESS) {
            printf("Done with JXL_DEC_SUCCESS\n");
            Py_RETURN_NONE;
        } else if (status == JXL_DEC_NEED_MORE_INPUT) {
            status = JxlDecoderSetInput(decoder, jxl_data, jxl_data_len);
            JxlDecoderCloseInput(decoder);
        } else if (status == JXL_DEC_FRAME) {
            status = JxlDecoderGetFrameHeader(decoder, &fhdr);
            continue;
        }
    }
    printf("Done\n");

    return Py_True;
}

PyObject *
_jxl_decoder_get_info(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    return Py_BuildValue(
        "(II)sOIIII",
        decp->basic_info.xsize,
        decp->basic_info.ysize,
        decp->mode,
        decp->basic_info.have_animation ? Py_True : Py_False,
        decp->basic_info.animation.tps_numerator,
        decp->basic_info.animation.tps_denominator,
        decp->basic_info.animation.num_loops,
        decp->n_frames
    );
}

PyObject *
_jxl_decoder_get_next(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;
    PyObject *bytes;
    PyObject *ret;
    JxlFrameHeader fhdr = {};

    char *jxl_call_name;

    printf("torchget_next %d\n", decp->status);
    // process events until next frame output is ready
    while (decp->status != JXL_DEC_NEED_IMAGE_OUT_BUFFER) {
        decp->status = JxlDecoderProcessInput(decp->decoder);
        printf("status %d\n", decp->status);

        // every frame was decoded successfully
        if (decp->status == JXL_DEC_SUCCESS) {
            printf("torchnone\n");
            Py_RETURN_NONE;
        }

        if (decp->status == JXL_DEC_FRAME) {
            // decode frame header
            decp->status = JxlDecoderGetFrameHeader(decp->decoder, &fhdr);
            continue;
        }
    }

    size_t new_outbuf_len;
    decp->status = JxlDecoderImageOutBufferSize(
        decp->decoder, &decp->pixel_format, &new_outbuf_len
    );

    // only allocate memory when current buffer is too small
    if (decp->outbuf_len < new_outbuf_len) {
        decp->outbuf_len = new_outbuf_len;
        uint8_t *_new_outbuf = realloc(decp->outbuf, decp->outbuf_len);
        decp->outbuf = _new_outbuf;
    }

    decp->status = JxlDecoderSetImageOutBuffer(
        decp->decoder, &decp->pixel_format, decp->outbuf, decp->outbuf_len
    );

    // decode image into output_buffer
    decp->status = JxlDecoderProcessInput(decp->decoder);

    bytes = PyBytes_FromStringAndSize((char *)(decp->outbuf), decp->outbuf_len);

    printf("torchsuccess\n");
    ret = Py_BuildValue("SIi", bytes, fhdr.duration, fhdr.is_last);

    Py_DECREF(bytes);
    return ret;

    // we also shouldn't reach here if frame read was ok

    // set error message
    char err_msg[128];

end:
    snprintf(
        err_msg,
        128,
        "could not read frame. libjxl call: %s returned: %d",
        jxl_call_name,
        decp->status
    );
    PyErr_SetString(PyExc_OSError, err_msg);

    return NULL;
}

PyObject *
_jxl_decoder_get_icc(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    if (!decp->jxl_icc) {
        Py_RETURN_NONE;
    }

    return PyBytes_FromStringAndSize((const char *)decp->jxl_icc, decp->jxl_icc_len);
}

PyObject *
_jxl_decoder_get_exif(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    if (!decp->jxl_exif) {
        Py_RETURN_NONE;
    }

    return PyBytes_FromStringAndSize((const char *)decp->jxl_exif, decp->jxl_exif_len);
}

PyObject *
_jxl_decoder_get_xmp(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    if (!decp->jxl_xmp) {
        Py_RETURN_NONE;
    }

    return PyBytes_FromStringAndSize((const char *)decp->jxl_xmp, decp->jxl_xmp_len);
}

// Version as string
const char *
JpegXlDecoderVersion_str(void) {
    static char version[20];
    sprintf(
        version,
        "%d.%d.%d",
        JPEGXL_MAJOR_VERSION,
        JPEGXL_MINOR_VERSION,
        JPEGXL_PATCH_VERSION
    );
    return version;
}

/* -------------------------------------------------------------------- */
/* Type Definitions                                                     */
/* -------------------------------------------------------------------- */

// JpegXlDecoder methods
static struct PyMethodDef _jpegxl_decoder_methods[] = {
    {"get_info", (PyCFunction)_jxl_decoder_get_info, METH_NOARGS, "get_info"},
    {"get_next", (PyCFunction)_jxl_decoder_get_next, METH_NOARGS, "get_next"},
    {"get_icc", (PyCFunction)_jxl_decoder_get_icc, METH_NOARGS, "get_icc"},
    {"get_exif", (PyCFunction)_jxl_decoder_get_exif, METH_NOARGS, "get_exif"},
    {"get_xmp", (PyCFunction)_jxl_decoder_get_xmp, METH_NOARGS, "get_xmp"},
    {"rewind", (PyCFunction)_jxl_decoder_rewind, METH_NOARGS, "rewind"},
    {NULL, NULL} /* sentinel */
};

// JpegXlDecoder type definition
static PyTypeObject JpegXlDecoder_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "JpegXlDecoder",
    .tp_basicsize = sizeof(JpegXlDecoderObject),
    .tp_dealloc = (destructor)_jxl_decoder_dealloc,
    .tp_methods = _jpegxl_decoder_methods,
};

/* -------------------------------------------------------------------- */
/* Module Setup                                                         */
/* -------------------------------------------------------------------- */

static PyMethodDef jpegxlMethods[] = {
    {"JpegXlDecoder", _jxl_decoder_new, METH_VARARGS, "JpegXlDecoder"}, {NULL, NULL}
};

static int
setup_module(PyObject *m) {
    if (PyType_Ready(&JpegXlDecoder_Type) < 0) {
        return -1;
    }

    // TODO(oloke) ready object types?
    PyObject *d = PyModule_GetDict(m);
    PyObject *v = PyUnicode_FromString(JpegXlDecoderVersion_str());
    PyDict_SetItemString(d, "libjxl_version", v ? v : Py_None);
    Py_XDECREF(v);

    return 0;
}

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, setup_module},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

PyMODINIT_FUNC
PyInit__jpegxl(void) {
    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_jpegxl",
        .m_methods = jpegxlMethods,
        .m_slots = slots
    };

    return PyModuleDef_Init(&module_def);
}
