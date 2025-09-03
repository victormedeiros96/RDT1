from setuptools import setup
from Cython.Build import cythonize
import numpy # Precisamos incluir os cabeçalhos do NumPy

# Define o que será compilado.
# Neste caso, nosso script de processamento de imagem.
ext_modules = cythonize(
    "Core/processing_script.py",
    compiler_directives={'language_level' : "3"} # Garante compatibilidade com Python 3
)

setup(
    ext_modules=ext_modules,
    include_dirs=[numpy.get_include()] # Adiciona os includes do NumPy para a compilação
)