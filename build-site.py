from pathlib import Path
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
    return None # (ASSETS_PATH / 'does-not-compile.html').relative_to('_site')
  else:
    path.with_suffix('.pdf').rename(rendered_path)
    return rendered_path.relative_to('_site')

def lecture(name, title):
  return {'type': 'lecture',  'title': title, 'href': rendered(Path('machine-learning-theory') / 'lectures' / (name + '-lecture.Rnw'))}

def homework(name, title, due):
  return {'type': 'homework', 'title': title, 
          'due':  due.strftime("%a, %b %d"),
          'href': rendered(Path('machine-learning-theory') / 'homework' / (name + '-homework.Rnw'))}

def review(title=""):
  return {'type': 'review', 'title': title}


def lab(name, title, warmup=None, followup=None, displaytype='Lab'):
  nbname = name + '-lab.ipynb'
  output_path = ASSETS_PATH / 'labs' / nbname
  parent = Path('machine-learning-theory') / 'labs'
  
  if not (output_path.exists() and output_path.stat().st_mtime > (parent / nbname).stat().st_mtime):
    nboutput=subprocess.run(['jupyter', 'nbconvert', '--clear-output', '--to', 'notebook', nbname,  
                           '--output',  output_path.resolve().with_suffix(''), 
		                       '--TagRemovePreprocessor.enabled=True', '--TagRemovePreprocessor.remove_cell_tags', 'solution'], cwd=parent)
    htmloutput=None and subprocess.run(['jupyter', 'nbconvert', '--to', 'html', '--template', 'classic', '--embed-images', nbname, 
                           '--output',  output_path.resolve().with_suffix(''), 
                           '--Highlight2HTML.extra_formatter_options', 'linenos=table',
		                       '--TagRemovePreprocessor.enabled=True', '--TagRemovePreprocessor.remove_cell_tags', 'solution'], cwd=parent)
  
  def rel_or_none(path): return path.relative_to('_site') if path.exists() else None
  return {'type': 'lab', 'displaytype': displaytype, 'title': title, 
          'notebook': rel_or_none(output_path), 
          'html':     rel_or_none(output_path.with_suffix('.html')), 
          'warmup': warmup, 
          'followup': followup }
  

def dayoff(title):
  return {'type': 'dayoff', 'title': title}

# Describe the Syllabus

from datetime import date, datetime
from dateutil.rrule import rrule, WEEKLY, SU, TU, TH
from dateutil.relativedelta import relativedelta

def sunday_of_week(day): 
  return day + relativedelta(weekday=SU(-1))

def group_by_week(days):
  sundays = { sunday_of_week(day) for day in days }
  return [ [{'date': day.strftime("%a, %b %d")} | activity for day,activity in sorted(days.items()) if sunday_of_week(day) == sunday]  for sunday in sorted(sundays) ]


startdate = date(2025, 1, 14)
enddate = date(2025, 4, 25)
daysoff = { 
  datetime(2025, 3, 11): dayoff('Spring Break'),
  datetime(2025, 3, 13): dayoff('Spring Break')
}

classdays = [day for day in rrule(WEEKLY, dtstart=startdate, until=enddate, byweekday=(TU, TH)) if day not in daysoff]
activities = [
  lecture('intro', 'Introduction'),
  lab('monotone', 'Implementing Monotone Regression (1/2)', warmup=lab('fitting-lines-in-CVXR', 'Fitting Lines in CVXR', displaytype='Warm Up')),
  lab('monotone', 'Implementing Monotone Regression (2/2)', followup=lab('image-denoising',     'Image Denoising',       displaytype='Follow Up')),
  lecture('bounded-variation', 'Bounded Variation Regression'),
  lab('bounded-variation',     'Implementing Bounded Variation Regression'),
  lab('convergence-rates',     'Rates of Convergence'),
  lecture('r-learner',         'Treatment Effects and the R-Learner'),
  lab('r-learner-parametric',    'The Parametric R-Learner'),
  lab('r-learner-nonparametric', 'The Nonparametric R-Learner'), 
  review(), 
  
  lecture('sobolev-regression', 'Sobolev Regression (1/2)'),
  lecture('sobolev-regression', 'Sobolev Regression (2/2)'),
  lab('sobolev-regression', 'Implementing Sobolev Regression'),
  review(), 
  
  lecture('multivariate-sobolev', 'Multivariate Sobolev Regression'),
  lab('image-denoising',          'Image Denoising'),
  lecture('least-squares-finite-models', 'Least Squares in Finite Models, i.e. Model Selection (1/2)'),
  lecture('least-squares-finite-models', 'Least Squares in Finite Models, i.e. Model Selection (2/2)'),
  lecture('least-squares-infinite-models', 'Least Squares in Infinite Models, i.e. Regression, with Gaussian Noise'),
  review('+ Misspecification'),
  lab('drawing-width',   'Drawing Gaussian Width'),
  lab('computing-width', 'Computing Gaussian Width'),

  lecture('covering-numbers', 'Bounding Gaussian Width using Covering Numbers'),
  lecture('chaining',         'Bounding Gaussian Width using Chaining'),
  lecture('curse',            'The Curse of Dimensionality'),
  review(),
  lecture('non-gaussian',     'Least Squares and non-Gaussian Noise'),
  lecture('sampling',         'Least Squares, Sampling, and Population MSE'),
]
homeworks = {
  0: [homework('vector-spaces', 'Vector Spaces',                   due=datetime(2025, 1, 23))],
  1: [homework('inner-product-spaces', 'Inner Product Spaces',     due=datetime(2025, 1, 30))],
  #2: [homework('smooth-regression', 'Option 1. Smooth Regression', due=datetime(2025, 2, 6)),
  #    homework('convex-regression', 'Option 2. Convex Regression', due=datetime(2025, 2, 6))],
}
    
def censor(day, activity):
  if day >= sunday_of_week(datetime.now()) + relativedelta(weeks=1):
    return activity | {'href': None, 'notebook': None, 'html': None}
  else:
    return activity

days = daysoff | { day: censor(day,activity) for day, activity in zip(classdays, activities) }

weeks = group_by_week(days)
for week, options in homeworks.items():
  for assignment in options:
    weeks[week].append( assignment ) 

# Render the Index Page
from pybars import Compiler

compiler = Compiler()
template = compiler.compile(open("templates/spring25.mustache", "r").read())
partials = {x : compiler.compile(open(f"templates/{x}.mustache", "r").read()) for x in ['lecture', 'homework', 'lab', 'review', 'dayoff', 'notebook']}
output = template( {'weeks' : weeks }, partials=partials)
open('_site/index.html', 'w').write(output)
