/*
 * PIL FreeType Driver
 *
 * a FreeType 2.X driver for PIL
 *
 * history:
 * 2001-02-17 fl  Created (based on old experimental freetype 1.0 code)
 * 2001-04-18 fl  Fixed some egcs compiler nits
 * 2002-11-08 fl  Added unicode support; more font metrics, etc
 * 2003-05-20 fl  Fixed compilation under 1.5.2 and newer non-unicode builds
 * 2003-09-27 fl  Added charmap encoding support
 * 2004-05-15 fl  Fixed compilation for FreeType 2.1.8
 * 2004-09-10 fl  Added support for monochrome bitmaps
 * 2006-06-18 fl  Fixed glyph bearing calculation
 * 2007-12-23 fl  Fixed crash in family/style attribute fetch
 * 2008-01-02 fl  Handle Unicode filenames properly
 *
 * Copyright (c) 1998-2007 by Secret Labs AB
 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "Imaging.h"

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_GLYPH_H

#define KEEP_PY_UNICODE
#include "py3.h"

#if !defined(_MSC_VER) && !defined(__MINGW32__)
#include <dlfcn.h>
#endif

#if !defined(FT_LOAD_TARGET_MONO)
#define FT_LOAD_TARGET_MONO  FT_LOAD_MONOCHROME
#endif


static struct PyGetSetDef font_getsetters[] = {
    { NULL }
};

static PyMethodDef _functions[] = {
    {NULL, NULL}
};

static int
setup_module(PyObject* m) {
    PyObject* d;

    d = PyModule_GetDict(m);

    return 0;
}

#if PY_VERSION_HEX >= 0x03000000
PyMODINIT_FUNC
PyInit__imagingft(void) {
    PyObject* m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_imagingft",       /* m_name */
        NULL,               /* m_doc */
        -1,                 /* m_size */
        _functions,         /* m_methods */
    };

    m = PyModule_Create(&module_def);

    if (setup_module(m) < 0)
        return NULL;

    return m;
}
#else
PyMODINIT_FUNC
init_imagingft(void)
{
    PyObject* m = Py_InitModule("_imagingft", _functions);
    setup_module(m);
}
#endif


