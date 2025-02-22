/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for ZIP (deflated) image data.
 *
 * history:
 * 1996-12-14 fl   Created (for PNG)
 * 1997-01-15 fl   Prepared to read TIFF/ZIP
 * 2001-11-19 fl   PNG incomplete read patch (from Bernhard Herzog)
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997-2001.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#ifdef HAVE_LIBZ

#include "ZipCodecs.h"

static const int OFFSET[] = {7, 3, 3, 1, 1, 0, 0};
static const int STARTING_COL[] = {0, 4, 0, 2, 0, 1, 0};
static const int STARTING_ROW[] = {0, 0, 4, 0, 2, 0, 1};
static const int COL_INCREMENT[] = {8, 8, 4, 4, 2, 2, 1};
static const int ROW_INCREMENT[] = {8, 8, 8, 4, 4, 2, 2};

/* Get the length in bytes of a scanline in the pass specified,
 * for interlaced images */
static int
get_row_len(ImagingCodecState state, int pass) {
    int row_len = (state->xsize + OFFSET[pass]) / COL_INCREMENT[pass];
    return ((row_len * state->bits) + 7) / 8;
}

/* -------------------------------------------------------------------- */
/* Decoder                                                              */
/* -------------------------------------------------------------------- */

int
ImagingZipDecode(Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    z_stream z_stream;
    z_stream.zalloc = (alloc_func)NULL;
    z_stream.zfree = (free_func)NULL;
    z_stream.opaque = (voidpf)NULL;

    printf("Before segfault\n");
    inflateInit(&z_stream);
    printf("After segfault\n");
    return -1;
}

int
ImagingZipDecodeCleanup(ImagingCodecState state) {
    /* called to free the decompression engine when the decode terminates
       due to a corrupt or truncated image
    */
    ZIPSTATE *context = (ZIPSTATE *)state->context;

    /* Clean up */
    if (context->previous) {
        inflateEnd(&context->z_stream);
        free(context->previous);
        context->previous = NULL;
    }
    return -1;
}

#endif
