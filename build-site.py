from pathlib import Path
from pybars import Compiler
import math
import subprocess
import yaml

ASSETS_PATH = Path('_site/assets')
def rendered(path, dash_whatever=''):
  rendered_path = (ASSETS_PATH / path.relative_to('machine-learning-theory').parent / (path.with_suffix('').name + dash_whatever)).with_suffix('.pdf') 
  if (rendered_path.exists() and rendered_path.stat().st_mtime > path.stat().st_mtime):
    return rendered_path.relative_to('_site')
  print(f"rendering {rendered_path.name}")
  output=subprocess.run(['latexmk', path.name], cwd=path.parent)
  if output.returncode:
    return (ASSETS_PATH / 'does-not-compile.html').relative_to('_site')
  else:
    path.with_suffix('.pdf').rename(rendered_path)
    return rendered_path.relative_to('_site')

def lecture(name):
  return rendered(Path('machine-learning-theory') / 'lectures' / (name + '-lecture.Rnw'))

def homework(name):
  return rendered(Path('machine-learning-theory') / 'homework' / (name + '-homework.Rnw'))

# Materials
units = [
  {
    'unit': 'Fitting Regression Models',
    'lectures': [ 
      { 'name': 'Introduction', 'url': lecture('intro') },
      { 'name': 'Bounded Variation Regression', 'url': lecture('bounded-variation') },
      { 'name': 'Treatment Effects and the R-Learner', 'url': lecture('r-learner') },
      { 'name': 'Sobolev Regression', 'url': lecture('sobolev-regression') },
      { 'name': 'Multivariate Sobolev Regression', 'url': lecture('isotropic-sobolev') }
    ],
    'homework': [
      { 'name': 'Vector Spaces', 'url': homework('vector-spaces') },
      { 'name': 'Convex Regression', 'url': homework('convex-regression') },
      { 'name': 'Lipschitz Regression', 'url': homework('smoothness') },
      { 'name': 'Polynomial Regression and the Gaussian Sobolev Model', 'url': homework('gaussian-sobolev-model') }
    ]
  },{ 
    'unit': 'Simplified Least Squares Theory',
    'lectures': [
      { 'name': 'Least Squares in Finite Models', 'url': lecture('least-squares-finite-models') },
      { 'name': 'Least Squares in Infinite Models', 'url': lecture('least-squares-infinite-models') },
      { 'name': 'Bounding Gaussian Width using Covering Numbers', 'url': lecture('covering-numbers') },
      { 'name': 'Bounding Gaussian Width using Chaining', 'url': lecture('chaining') }
    ],
    'homework': [
      {'name': 'Subgaussianity and Maximal Inequalities', 'url': homework('tail-bounds')},
      {'name': 'Calculating Gaussian Width', 'url': homework('gaussian-width')},
      {'name': 'The Gaussian Width of Sobolev Models', 'url': homework('sobolev-models')},
      {'name': 'Covering Numbers for Monotone and BV Regression Models', 'url': homework('covering-numbers')} 
    ]
  },{ 
    'unit': 'Broadening the Scope',
    'lectures': [
      {'name': 'Misspecification', 'url': lecture('least-squares-misspecified')},
      {'name': 'Non-Gaussian Noise', 'url': lecture('least-squares-misspecified')},
      {'name': 'Sampling and Population MSE', 'url': lecture('least-squares-population')}
    ],
    'homework': [
      { 'name': 'Misspecification', 'url': homework('misspecification')},
      { 'name': 'Comparing Gaussian and Non-Gaussian Noise', 'url': homework('width-comparison')}
    ]
   }
]


# Render the Index Page
compiler = Compiler()
source = open("index.template", "r").read()
template = compiler.compile(source)
output = template( {'units': units } )
open('_site/index.html', 'w').write(output)
