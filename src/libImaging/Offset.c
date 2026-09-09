/*
 * The Python Imaging Library
 * $Id$
 *
 * offset an image in x and y directions
 *
 * history:
 * 96-07-22 fl: Created
 * 98-11-01 cgw@pgt.com: Fixed negative-array index bug
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

/**
 * Copy `im` into a newly allocated image,
 * wrapping every pixel by (xoffset, yoffset) modulo the image size.
 *
 * Contract: im is read-only.
 */
Imaging
ImagingOffset(Imaging im, int xoffset, int yoffset) {
    if (!im) {
        return (Imaging)ImagingError_ModeError();
    }

    int xsize = im->xsize, ysize = im->ysize;

    Imaging imOut = ImagingNewDirty(im->mode, xsize, ysize);
    if (!imOut) {
        return NULL;
    }

    ImagingCopyPalette(imOut, im);

    /* make offsets positive to avoid negative coordinates */
    if (xsize == 0 || ysize == 0) {
        return imOut;
    }
    xoffset %= xsize;
    xoffset = xsize - xoffset;
    if (xoffset < 0) {
        xoffset += xsize;
    }

    yoffset %= ysize;
    yoffset = ysize - yoffset;
    if (yoffset < 0) {
        yoffset += ysize;
    }

    // yi depends only on y, so compute it (and both row pointers) once per
    // row instead of redoing the modulo and pointer chase for every x.
#define OFFSET(type, image)                           \
    for (int y = 0; y < ysize; y++) {                 \
        int yi = (y + yoffset) % ysize;               \
        type *restrict in = (type *)im->image[yi];    \
        type *restrict out = (type *)imOut->image[y]; \
        for (int x = 0; x < xsize; x++) {             \
            int xi = (x + xoffset) % xsize;           \
            out[x] = in[xi];                          \
        }                                             \
    }

    if (im->image8) {
        if (im->pixelsize == 2) {
            OFFSET(UINT16, image8)
        } else {
            OFFSET(UINT8, image8)
        }
    } else {
        OFFSET(INT32, image32)
    }

    return imOut;
}
