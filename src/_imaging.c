#define PY_SSIZE_T_CLEAN
#include "Python.h"

#include "zlib.h"

static PyMethodDef functions[] = {
    {NULL, NULL} /* sentinel */
};

static int
setup_module(PyObject *m) {
    z_stream z_stream;
    z_stream.zalloc = (alloc_func)NULL;
    z_stream.zfree = (free_func)NULL;
    z_stream.opaque = (voidpf)NULL;

    printf("Before segfault\n");
    inflateInit(&z_stream);
    printf("After segfault\n");

    return 0;
}

PyMODINIT_FUNC
PyInit__imaging(void) {
    PyObject *m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_imaging",
        .m_size = -1,
        .m_methods = functions,
    };

    m = PyModule_Create(&module_def);

    if (setup_module(m) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
