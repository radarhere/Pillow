/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for JPEG2000 image data.
 *
 * history:
 * 2014-03-12 ajh  Created
 *
 * Copyright (c) 2014 Coriolis Systems Limited
 * Copyright (c) 2014 Alastair Houghton
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

#ifdef HAVE_OPENJPEG

#include <stdlib.h>
#include "Jpeg2K.h"

typedef struct {
    OPJ_UINT32 tile_index;
    OPJ_UINT32 data_size;
    OPJ_INT32 x0, y0, x1, y1;
    OPJ_UINT32 nb_comps;
} JPEG2KTILEINFO;

/* -------------------------------------------------------------------- */
/* Error handler                                                        */
/* -------------------------------------------------------------------- */

static void
j2k_error(const char *msg, void *client_data) {
    JPEG2KDECODESTATE *state = (JPEG2KDECODESTATE *)client_data;
    free((void *)state->error_msg);
    state->error_msg = strdup(msg);
}

/* -------------------------------------------------------------------- */
/* Buffer input stream                                                  */
/* -------------------------------------------------------------------- */

static OPJ_SIZE_T
j2k_read(void *p_buffer, OPJ_SIZE_T p_nb_bytes, void *p_user_data) {
    int data[] = {-1, 79, -1, 81, 0, 47, 0, 0, 0, 96, 0, 25, 0, 0, 0, 3, 0, 0, 0, 32, 0, 0, 0, 0, 0, 107, 0, 0, 0, 0, 0, 3, 0, 0, 0, 21, 0, 0, 0, 0, 0, 3, 8, 44, -9, 7, 60, 4, 0, 39, -1, -1, 82, 0, 13, 5, 0, 47, -112, 1, 0, 0, 0, 0, 0, -127, -1, 92, 0, 4, 96, 49, -1, -112, 0, 10, 0, 0, 0, 0, 0, 15, 0, 1, -1, -109, -1};
    for (int i = 0; i < 87; i++ ) {
      ((char *)p_buffer)[i] = data[i];
    }
    return 87;
}

/* -------------------------------------------------------------------- */
/* Unpackers                                                            */
/* -------------------------------------------------------------------- */

typedef void (*j2k_unpacker_t)(
    opj_image_t *in, const JPEG2KTILEINFO *tileInfo, const UINT8 *data, Imaging im
);

struct j2k_decode_unpacker {
    const char *mode;
    OPJ_COLOR_SPACE color_space;
    unsigned components;
    /* bool indicating if unpacker supports subsampling */
    int subsampling;
    j2k_unpacker_t unpacker;
};

static inline unsigned
j2ku_shift(unsigned x, int n) {
    if (n < 0) {
        return x >> -n;
    } else {
        return x << n;
    }
}

static void
j2ku_gray_l(
    opj_image_t *in, const JPEG2KTILEINFO *tileinfo, const UINT8 *tiledata, Imaging im
) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int csiz = (in->comps[0].prec + 7) >> 3;

    unsigned x, y;

    if (csiz == 3) {
        csiz = 4;
    }

    if (shift < 0) {
        offset += 1 << (-shift - 1);
    }

    /* csiz*h*w + offset = tileinfo.datasize */
    switch (csiz) {
        case 1:
            for (y = 0; y < h; ++y) {
                const UINT8 *data = &tiledata[y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
        case 2:
            for (y = 0; y < h; ++y) {
                const UINT16 *data = (const UINT16 *)&tiledata[2 * y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
        case 4:
            for (y = 0; y < h; ++y) {
                const UINT32 *data = (const UINT32 *)&tiledata[4 * y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
    }
}

static void
j2ku_gray_i(
    opj_image_t *in, const JPEG2KTILEINFO *tileinfo, const UINT8 *tiledata, Imaging im
) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shift = 16 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int csiz = (in->comps[0].prec + 7) >> 3;

    unsigned x, y;

    if (csiz == 3) {
        csiz = 4;
    }

    if (shift < 0) {
        offset += 1 << (-shift - 1);
    }

    switch (csiz) {
        case 1:
            for (y = 0; y < h; ++y) {
                const UINT8 *data = &tiledata[y * w];
                UINT16 *row = (UINT16 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
        case 2:
            for (y = 0; y < h; ++y) {
                const UINT16 *data = (const UINT16 *)&tiledata[2 * y * w];
                UINT16 *row = (UINT16 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    UINT16 pixel = j2ku_shift(offset + *data++, shift);
#ifdef WORDS_BIGENDIAN
                    pixel = (pixel >> 8) | (pixel << 8);
#endif
                    *row++ = pixel;
                }
            }
            break;
        case 4:
            for (y = 0; y < h; ++y) {
                const UINT32 *data = (const UINT32 *)&tiledata[4 * y * w];
                UINT16 *row = (UINT16 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
    }
}

static void
j2ku_gray_rgb(
    opj_image_t *in, const JPEG2KTILEINFO *tileinfo, const UINT8 *tiledata, Imaging im
) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int csiz = (in->comps[0].prec + 7) >> 3;

    unsigned x, y;

    if (shift < 0) {
        offset += 1 << (-shift - 1);
    }

    if (csiz == 3) {
        csiz = 4;
    }

    switch (csiz) {
        case 1:
            for (y = 0; y < h; ++y) {
                const UINT8 *data = &tiledata[y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    UINT8 byte = j2ku_shift(offset + *data++, shift);
                    row[0] = row[1] = row[2] = byte;
                    row[3] = 0xff;
                    row += 4;
                }
            }
            break;
        case 2:
            for (y = 0; y < h; ++y) {
                const UINT16 *data = (UINT16 *)&tiledata[2 * y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    UINT8 byte = j2ku_shift(offset + *data++, shift);
                    row[0] = row[1] = row[2] = byte;
                    row[3] = 0xff;
                    row += 4;
                }
            }
            break;
        case 4:
            for (y = 0; y < h; ++y) {
                const UINT32 *data = (UINT32 *)&tiledata[4 * y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    UINT8 byte = j2ku_shift(offset + *data++, shift);
                    row[0] = row[1] = row[2] = byte;
                    row[3] = 0xff;
                    row += 4;
                }
            }
            break;
    }
}

static void
j2ku_graya_la(
    opj_image_t *in, const JPEG2KTILEINFO *tileinfo, const UINT8 *tiledata, Imaging im
) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int csiz = (in->comps[0].prec + 7) >> 3;
    int ashift = 8 - in->comps[1].prec;
    int aoffset = in->comps[1].sgnd ? 1 << (in->comps[1].prec - 1) : 0;
    int acsiz = (in->comps[1].prec + 7) >> 3;
    const UINT8 *atiledata;

    unsigned x, y;

    if (csiz == 3) {
        csiz = 4;
    }
    if (acsiz == 3) {
        acsiz = 4;
    }

    if (shift < 0) {
        offset += 1 << (-shift - 1);
    }
    if (ashift < 0) {
        aoffset += 1 << (-ashift - 1);
    }

    atiledata = tiledata + csiz * w * h;

    for (y = 0; y < h; ++y) {
        const UINT8 *data = &tiledata[csiz * y * w];
        const UINT8 *adata = &atiledata[acsiz * y * w];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (x = 0; x < w; ++x) {
            UINT32 word = 0, aword = 0, byte;

            switch (csiz) {
                case 1:
                    word = *data++;
                    break;
                case 2:
                    word = *(const UINT16 *)data;
                    data += 2;
                    break;
                case 4:
                    word = *(const UINT32 *)data;
                    data += 4;
                    break;
            }

            switch (acsiz) {
                case 1:
                    aword = *adata++;
                    break;
                case 2:
                    aword = *(const UINT16 *)adata;
                    adata += 2;
                    break;
                case 4:
                    aword = *(const UINT32 *)adata;
                    adata += 4;
                    break;
            }

            byte = j2ku_shift(offset + word, shift);
            row[0] = row[1] = row[2] = byte;
            row[3] = j2ku_shift(aoffset + aword, ashift);
            row += 4;
        }
    }
}

static void
j2ku_srgb_rgb(
    opj_image_t *in, const JPEG2KTILEINFO *tileinfo, const UINT8 *tiledata, Imaging im
) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shifts[3], offsets[3], csiz[3];
    unsigned dx[3], dy[3];
    const UINT8 *cdata[3];
    const UINT8 *cptr = tiledata;
    unsigned n, x, y;

    for (n = 0; n < 3; ++n) {
        cdata[n] = cptr;
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        csiz[n] = (in->comps[n].prec + 7) >> 3;
        dx[n] = (in->comps[n].dx);
        dy[n] = (in->comps[n].dy);

        if (csiz[n] == 3) {
            csiz[n] = 4;
        }

        if (shifts[n] < 0) {
            offsets[n] += 1 << (-shifts[n] - 1);
        }

        cptr += csiz[n] * (w / dx[n]) * (h / dy[n]);
    }

    for (y = 0; y < h; ++y) {
        const UINT8 *data[3];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (n = 0; n < 3; ++n) {
            data[n] = &cdata[n][csiz[n] * (y / dy[n]) * (w / dx[n])];
        }

        for (x = 0; x < w; ++x) {
            for (n = 0; n < 3; ++n) {
                UINT32 word = 0;

                switch (csiz[n]) {
                    case 1:
                        word = data[n][x / dx[n]];
                        break;
                    case 2:
                        word = ((const UINT16 *)data[n])[x / dx[n]];
                        break;
                    case 4:
                        word = ((const UINT32 *)data[n])[x / dx[n]];
                        break;
                }

                row[n] = j2ku_shift(offsets[n] + word, shifts[n]);
            }
            row[3] = 0xff;
            row += 4;
        }
    }
}

static void
j2ku_sycc_rgb(
    opj_image_t *in, const JPEG2KTILEINFO *tileinfo, const UINT8 *tiledata, Imaging im
) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shifts[3], offsets[3], csiz[3];
    unsigned dx[3], dy[3];
    const UINT8 *cdata[3];
    const UINT8 *cptr = tiledata;
    unsigned n, x, y;

    for (n = 0; n < 3; ++n) {
        cdata[n] = cptr;
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        csiz[n] = (in->comps[n].prec + 7) >> 3;
        dx[n] = (in->comps[n].dx);
        dy[n] = (in->comps[n].dy);

        if (csiz[n] == 3) {
            csiz[n] = 4;
        }

        if (shifts[n] < 0) {
            offsets[n] += 1 << (-shifts[n] - 1);
        }

        cptr += csiz[n] * (w / dx[n]) * (h / dy[n]);
    }

    for (y = 0; y < h; ++y) {
        const UINT8 *data[3];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        UINT8 *row_start = row;
        for (n = 0; n < 3; ++n) {
            data[n] = &cdata[n][csiz[n] * (y / dy[n]) * (w / dx[n])];
        }

        for (x = 0; x < w; ++x) {
            for (n = 0; n < 3; ++n) {
                UINT32 word = 0;

                switch (csiz[n]) {
                    case 1:
                        word = data[n][x / dx[n]];
                        break;
                    case 2:
                        word = ((const UINT16 *)data[n])[x / dx[n]];
                        break;
                    case 4:
                        word = ((const UINT32 *)data[n])[x / dx[n]];
                        break;
                }

                row[n] = j2ku_shift(offsets[n] + word, shifts[n]);
            }
            row[3] = 0xff;
            row += 4;
        }

        ImagingConvertYCbCr2RGB(row_start, row_start, w);
    }
}

static void
j2ku_srgba_rgba(
    opj_image_t *in, const JPEG2KTILEINFO *tileinfo, const UINT8 *tiledata, Imaging im
) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shifts[4], offsets[4], csiz[4];
    unsigned dx[4], dy[4];
    const UINT8 *cdata[4];
    const UINT8 *cptr = tiledata;
    unsigned n, x, y;

    for (n = 0; n < 4; ++n) {
        cdata[n] = cptr;
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        csiz[n] = (in->comps[n].prec + 7) >> 3;
        dx[n] = (in->comps[n].dx);
        dy[n] = (in->comps[n].dy);

        if (csiz[n] == 3) {
            csiz[n] = 4;
        }

        if (shifts[n] < 0) {
            offsets[n] += 1 << (-shifts[n] - 1);
        }

        cptr += csiz[n] * (w / dx[n]) * (h / dy[n]);
    }

    for (y = 0; y < h; ++y) {
        const UINT8 *data[4];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (n = 0; n < 4; ++n) {
            data[n] = &cdata[n][csiz[n] * (y / dy[n]) * (w / dx[n])];
        }

        for (x = 0; x < w; ++x) {
            for (n = 0; n < 4; ++n) {
                UINT32 word = 0;

                switch (csiz[n]) {
                    case 1:
                        word = data[n][x / dx[n]];
                        break;
                    case 2:
                        word = ((const UINT16 *)data[n])[x / dx[n]];
                        break;
                    case 4:
                        word = ((const UINT32 *)data[n])[x / dx[n]];
                        break;
                }

                row[n] = j2ku_shift(offsets[n] + word, shifts[n]);
            }
            row += 4;
        }
    }
}

static void
j2ku_sycca_rgba(
    opj_image_t *in, const JPEG2KTILEINFO *tileinfo, const UINT8 *tiledata, Imaging im
) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shifts[4], offsets[4], csiz[4];
    unsigned dx[4], dy[4];
    const UINT8 *cdata[4];
    const UINT8 *cptr = tiledata;
    unsigned n, x, y;

    for (n = 0; n < 4; ++n) {
        cdata[n] = cptr;
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        csiz[n] = (in->comps[n].prec + 7) >> 3;
        dx[n] = (in->comps[n].dx);
        dy[n] = (in->comps[n].dy);

        if (csiz[n] == 3) {
            csiz[n] = 4;
        }

        if (shifts[n] < 0) {
            offsets[n] += 1 << (-shifts[n] - 1);
        }

        cptr += csiz[n] * (w / dx[n]) * (h / dy[n]);
    }

    for (y = 0; y < h; ++y) {
        const UINT8 *data[4];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        UINT8 *row_start = row;
        for (n = 0; n < 4; ++n) {
            data[n] = &cdata[n][csiz[n] * (y / dy[n]) * (w / dx[n])];
        }

        for (x = 0; x < w; ++x) {
            for (n = 0; n < 4; ++n) {
                UINT32 word = 0;

                switch (csiz[n]) {
                    case 1:
                        word = data[n][x / dx[n]];
                        break;
                    case 2:
                        word = ((const UINT16 *)data[n])[x / dx[n]];
                        break;
                    case 4:
                        word = ((const UINT32 *)data[n])[x / dx[n]];
                        break;
                }

                row[n] = j2ku_shift(offsets[n] + word, shifts[n]);
            }
            row += 4;
        }

        ImagingConvertYCbCr2RGB(row_start, row_start, w);
    }
}

static const struct j2k_decode_unpacker j2k_unpackers[] = {
    {"L", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_l},
    {"P", OPJ_CLRSPC_SRGB, 1, 0, j2ku_gray_l},
    {"PA", OPJ_CLRSPC_SRGB, 2, 0, j2ku_graya_la},
    {"I;16", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_i},
    {"I;16B", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_i},
    {"LA", OPJ_CLRSPC_GRAY, 2, 0, j2ku_graya_la},
    {"RGB", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_rgb},
    {"RGB", OPJ_CLRSPC_GRAY, 2, 0, j2ku_gray_rgb},
    {"RGB", OPJ_CLRSPC_SRGB, 3, 1, j2ku_srgb_rgb},
    {"RGB", OPJ_CLRSPC_SYCC, 3, 1, j2ku_sycc_rgb},
    {"RGB", OPJ_CLRSPC_SRGB, 4, 1, j2ku_srgb_rgb},
    {"RGB", OPJ_CLRSPC_SYCC, 4, 1, j2ku_sycc_rgb},
    {"RGBA", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_rgb},
    {"RGBA", OPJ_CLRSPC_GRAY, 2, 0, j2ku_graya_la},
    {"RGBA", OPJ_CLRSPC_SRGB, 3, 1, j2ku_srgb_rgb},
    {"RGBA", OPJ_CLRSPC_SYCC, 3, 1, j2ku_sycc_rgb},
    {"RGBA", OPJ_CLRSPC_SRGB, 4, 1, j2ku_srgba_rgba},
    {"RGBA", OPJ_CLRSPC_SYCC, 4, 1, j2ku_sycca_rgba},
    {"CMYK", OPJ_CLRSPC_CMYK, 4, 1, j2ku_srgba_rgba},
};

/* -------------------------------------------------------------------- */
/* Decoder                                                              */
/* -------------------------------------------------------------------- */

enum {
    J2K_STATE_START = 0,
    J2K_STATE_DECODING = 1,
    J2K_STATE_DONE = 2,
    J2K_STATE_FAILED = 3,
};

struct State {
    UINT8 *buffer;
};

static int
j2k_decode_entry(Imaging im, ImagingCodecState state) {
    opj_stream_t *stream = NULL;
    opj_image_t *image = NULL;
    opj_codec_t *codec = NULL;
    opj_dparameters_t params;
    printf("start\n");
    struct State *state2 = malloc(sizeof(struct State));

    stream = opj_stream_create(OPJ_J2K_STREAM_CHUNK_SIZE, OPJ_TRUE);

    opj_stream_set_read_function(stream, j2k_read);

    opj_stream_set_user_data(stream, state2, NULL);

    opj_stream_set_user_data_length(stream, 87);

    opj_set_default_decoder_parameters(&params);
    params.cp_reduce = 0;
    params.cp_layer = 0;

    codec = opj_create_decompress(OPJ_CODEC_J2K);

    opj_setup_decoder(codec, &params);

    opj_read_header(stream, codec, &image);
    JPEG2KTILEINFO tile_info;
    OPJ_BOOL should_continue;

    opj_read_tile_header(
        codec,
        stream,
        &tile_info.tile_index,
        &tile_info.data_size,
        &tile_info.x0,
        &tile_info.y0,
        &tile_info.x1,
        &tile_info.y1,
        &tile_info.nb_comps,
        &should_continue
    );
    printf("data size %d\n", tile_info.data_size);

    return -1;
}

int
ImagingJpeg2KDecode(Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    if (bytes) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        return -1;
    }

    if (state->state == J2K_STATE_DONE || state->state == J2K_STATE_FAILED) {
        return -1;
    }

    if (state->state == J2K_STATE_START) {
        state->state = J2K_STATE_DECODING;

        return j2k_decode_entry(im, state);
    }

    if (state->state == J2K_STATE_DECODING) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        return -1;
    }
    return -1;
}

/* -------------------------------------------------------------------- */
/* Cleanup                                                              */
/* -------------------------------------------------------------------- */

int
ImagingJpeg2KDecodeCleanup(ImagingCodecState state) {
    JPEG2KDECODESTATE *context = (JPEG2KDECODESTATE *)state->context;

    if (context->error_msg) {
        free((void *)context->error_msg);
    }

    context->error_msg = NULL;

    return -1;
}

const char *
ImagingJpeg2KVersion(void) {
    return opj_version();
}

#endif /* HAVE_OPENJPEG */
