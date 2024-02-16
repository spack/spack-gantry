# fmt: off
pkg_mappings = {'py-torch': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 48000000000.0}, 'rust': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 35000000000.0}, 'py-tensorflow': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 32000000000.0}, 'py-torchaudio': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 32000000000.0}, 'py-jaxlib': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 29000000000.0}, 'nvhpc': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 24000000000.0}, 'paraview': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 24000000000.0}, 'llvm': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 21000000000.0}, 'dealii': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 19000000000.0}, 'mxnet': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 19000000000.0}, 'rocblas': {'build_jobs': 12, 'cpu_request': 12.0, 'mem_request': 19000000000.0}, 'ecp-data-vis-sdk': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'intel-tbb': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 15000000000.0}, 'llvm-amdgpu': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 15000000000.0}, 'salmon': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 15000000000.0}, 'trilinos': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'ascent': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'axom': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'cistem': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'cuda': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'dray': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'gcc': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'ginkgo': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'hdf5': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'kokkos-kernels': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'mfem': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'mpich': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'netlib-lapack': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'openblas': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'openfoam': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'openturns': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'raja': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'relion': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'rocsolver': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'rocsparse': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'strumpack': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'sundials': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'visit': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 12000000000.0}, 'vtk': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'vtk-h': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'vtk-m': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'hpx': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 9000000000.0}, 'slate': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 9000000000.0}, 'warpx': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 9000000000.0}, 'hipblas': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 8000000000.0}, 'rocfft': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 8000000000.0}, 'umpire': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 8000000000.0}, 'lbann': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 7000000000.0}, 'magma': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 7000000000.0}, 'mesa': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 7000000000.0}, 'qt': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 7000000000.0}, 'dyninst': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 6000000000.0}, 'precice': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 6000000000.0}, 'cmake': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 5000000000.0}, 'plumed': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 5000000000.0}, 'wrf': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 5000000000.0}, 'parallelio': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 3000000000.0}, 'adios2': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'amrex': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'archer': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'autoconf-archive': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'blt': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'boost': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'butterflypack': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'cabana': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'caliper': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'camp': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'chai': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'conduit': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'curl': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'datatransferkit': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'faodel': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'fortrilinos': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'gettext': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'gptune': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'heffte': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'hpctoolkit': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'hwloc': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'hydrogen': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'hypre': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'kokkos': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'lammps': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'lapackpp': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'legion': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'libxml2': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libzmq': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'llvm-openmp-ompt': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'mbedtls': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'mvapich2': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'netlib-scalapack': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'omega-h': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'openjpeg': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'openmpi': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'openpmd-api': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'pagmo2': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'papyrus': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'parsec': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'petsc': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'pumi': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-beniget': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-cinemasci': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'pygmo': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-ipython-genutils': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-packaging': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-petsc4py': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-scipy': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-statsmodels': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-warlock': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'py-warpx': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'slepc': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'slurm': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'sqlite': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'superlu-dist': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'tasmanian': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'tau': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'upcxx': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 4000000000.0}, 'zfp': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'oce': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 3000000000.0}, 'binutils': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'blaspp': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'double-conversion': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'eigen': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'fftw': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'libtool': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'nasm': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'pegtl': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'pdt': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 2000000000.0}, 'kokkos-nvcc-wrapper': {'build_jobs': 8, 'cpu_request': 8.0, 'mem_request': 1000000000.0}, 'ffmpeg': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 1000000000.0}, 'gperftools': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 1000000000.0}, 'samrai': {'build_jobs': 2, 'cpu_request': 2.0, 'mem_request': 1000000000.0}, 'alsa-lib': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'ant': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'antlr': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'argobots': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'automake': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'berkeley-db': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'bison': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'bzip2': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'czmq': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'darshan-util': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'diffutils': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'docbook-xml': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'exmcutils': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'expat': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'findutils': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'flit': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'freetype': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'gawk': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'gdbm': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'glib': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'gmake': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'gotcha': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'hpcviewer': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'jansson': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'json-c': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libbsd': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libedit': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libevent': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libfabric': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libffi': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libgcrypt': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libiconv': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libidn2': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libjpeg-turbo': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libmd': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libnrm': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libpciaccess': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libpng': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libsigsegv': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libsodium': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libunistring': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libunwind': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'libyaml': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'lua': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'lua-luaposix': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'lz4': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'm4': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'meson': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'metis': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'mpfr': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'ncurses': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'ninja': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'numactl': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'openjdk': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'openssh': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'openssl': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'papi': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'parallel-netcdf': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'pcre': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'pcre2': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'pdsh': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'perl': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'perl-data-dumper': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'pkgconf': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-alembic': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-cffi': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-cycler': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-decorator': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-idna': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-jsonschema': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-kiwisolver': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-mistune': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-pycparser': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-setuptools': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-setuptools-scm': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-six': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-testpath': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'py-wheel': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'qhull': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'readline': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'sed': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'snappy': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'superlu': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'swig': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'tar': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'tcl': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'texinfo': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'unzip': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'util-linux-uuid': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'util-macros': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'xz': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'yaml-cpp': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'zlib': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}, 'zstd': {'build_jobs': 1, 'cpu_request': 0.5, 'mem_request': 500000000.0}}
