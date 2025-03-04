from pathlib import Path
import math
import subprocess
import yaml

ASSETS_PATH = Path('_site/assets')
def exists_newer(maybe_newer_path, old_path):
  return maybe_newer_path.exists() and maybe_newer_path.stat().st_mtime > old_path.stat().st_mtime

def rendered(path, dash_whatever='', solution=False):
  rendered_path = (ASSETS_PATH / path.relative_to('machine-learning-theory').parent / (path.with_suffix('').name + dash_whatever)).with_suffix('.pdf') 
  
  if not path.exists():
    print(f"skipping {path.name} because it doesn't exist")
    return None
  if exists_newer(rendered_path, path):
    return rendered_path.relative_to('_site')

  print(f"rendering {rendered_path.name}")
  if (path.parent / 'solution-preamble.tex').exists() and (path.parent / 'assignment-preamble.tex').exists():
    preamble = 'solution-preamble.tex' if solution else 'assignment-preamble.tex'
    subprocess.run(['ln', '-sf', preamble, 'preamble.tex'], cwd=path.parent)
  output=subprocess.run(['latexmk', path.name, '-auxdir=aux'], cwd=path.parent)

  if output.returncode: 
    print(f"latexmk failed for {path.name}")
    return None 
  else:
    path.with_suffix('.pdf').rename(rendered_path)
    return rendered_path.relative_to('_site')

def lecture(name, title, warmup=None, followup=None):
  return {'type': 'lecture',  'title': title, 
          'href': rendered(Path('machine-learning-theory') / 'lectures' / (name + '-lecture.Rnw')),
          'warmup': warmup, 'followup': followup }

def homework(name, title, due, displaytype=None):
  assignment = {'type': 'homework', 
                'title': title, 
                'displaytype': displaytype,
                'due':  due.strftime("%a, %b %d"),
                'href': rendered(Path('machine-learning-theory') / 'homework' / (name + '-homework.Rnw')) }

  duetime = due.replace(hour=23, minute=59)
  if datetime.now() > duetime:
    assignment['solution-href'] = rendered(Path('machine-learning-theory') / 'homework' / (name + '-homework.Rnw'), dash_whatever='-solution', solution=True)
    
  return assignment

def review(title="", href=None):
  return {'type': 'review', 'title': title, 'href': href}


def lab(name, title, warmup=None, followup=None, displaytype='Lab'):
  nbname = name + '-lab.ipynb'
  output_path = ASSETS_PATH / 'labs' / nbname
  solution_output_path = ASSETS_PATH / 'labs' / (name + '-lab-solution.ipynb') 
  parent = Path('machine-learning-theory') / 'labs'
  
  if not (parent / nbname).exists():
    print(f"skipping {nbname} because it doesn't exist")
    return {'type': 'lab', 'displaytype': displaytype, 'title': title } 
  
  def renderlab(nbname, the_output_path, remove_tag, format):
    if format == 'notebook':
      nboutput=subprocess.run(['jupyter', 'nbconvert', '--clear-output', '--to', 'notebook', nbname,  
                           '--output',  the_output_path.resolve().with_suffix(''), 
		                       '--TagRemovePreprocessor.enabled=True', '--TagRemovePreprocessor.remove_cell_tags', remove_tag], cwd=parent)
    elif format == 'html':
      htmloutput=subprocess.run(['jupyter', 'nbconvert', '--to', 'html', '--execute', '--embed-images', nbname, 
                           '--output',  the_output_path.resolve().with_suffix(''), 
                           '--Highlight2HTML.extra_formatter_options', 'linenos=table',
		                       '--TagRemovePreprocessor.enabled=True', '--TagRemovePreprocessor.remove_cell_tags', remove_tag], cwd=parent) 
  
  if not exists_newer(output_path, parent / nbname): 
    print(f"rendering {nbname}")
    renderlab(nbname, output_path, remove_tag='solution', format='notebook') 
  if not exists_newer(solution_output_path, parent / nbname):
    print(f"rendering {nbname} solution")
    renderlab(nbname, solution_output_path, remove_tag='solution-template', format='notebook')

  def rel_or_none(path): return path.relative_to('_site') if path.exists() else None
  return {'type': 'lab', 'displaytype': displaytype, 'title': title, 
          'notebook': rel_or_none(output_path), 
          'html':     rel_or_none(output_path.with_suffix('.html')), 
          'solution-notebook': rel_or_none(solution_output_path),
          'solution-html':     rel_or_none(solution_output_path.with_suffix('.html')),
          'warmup': warmup, 
          'followup': followup }
  

def dayoff(title):
  return {'type': 'dayoff', 'title': title}

# Describe the Syllabus

from datetime import date, time, datetime
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
  datetime(2025, 3, 13): dayoff('Spring Break'),
  datetime(2025, 2, 13): dayoff('Cancelled'),
}

classdays = [day for day in rrule(WEEKLY, dtstart=startdate, until=enddate, byweekday=(TU, TH)) if day not in daysoff]
activities = [
  lecture('intro', 'Introduction'),
  lab('monotone', 'Implementing Monotone Regression (1/2)',  
      warmup=lab('fitting-lines-in-CVXR', 'Fitting Lines in CVXR', displaytype='Warm Up')),
  lab('monotone', 'Implementing Monotone Regression (2/2)',  
      followup=lab('image-denoising',     'Image Denoising',       displaytype='Follow Up')),
  lecture('bounded-variation', 'Bounded Variation Regression'),
  lab('bounded-variation',     'Implementing Bounded Variation Regression'),
  lab('convergence-rates',     'Rates of Convergence'),
  lecture('r-learner',         'Treatment Effects and the R-Learner'),
  lab('rlearner',    'The Parametric R-Learner'),
  lab('rlearner', 'The Nonparametric R-Learner'), 
  
  review('Smooth and Shape-Constrained Regression', href=lab('first-review', 'Not Used')['notebook']),
  review('Smooth and Shape-Constrained Regression', href=lab('first-review', 'Not Used')['notebook']),

  lecture('sobolev-regression', 'Sobolev Regression',
      followup=homework('gaussian-sobolev-models', 'Gaussian Sobolev Models and Polynomial Approximation (Follow Up Activity)', 
                        due=datetime.combine(startdate, time(0, 0)), displaytype='Follow Up')),
  lab('sobolev-regression', 'Implementing Sobolev Regression',
      followup=lab('sobolev-rates', 'Rates of Convergence for Sobolev Regression', displaytype='Follow Up')),
   
  # Do the union bound/gaussian maximal inequality + Chebyshev for HW before this. 
  lecture('least-squares-finite-models',   'Least Squares in Finite Models, i.e. Model Selection (1/2)'),
  lecture('least-squares-finite-models',   'Least Squares in Finite Models, i.e. Model Selection (2/2)'),

  
  # Do Efron-Stein + Width Calculations for HW around here
  lecture('least-squares-infinite-models', 'Least Squares in Infinite Models, i.e. Regression, with Gaussian Noise'),
  lecture('least-squares-misspecification', 'Least Squares with Misspecification'),

  # Do drawing models in 2D (monotone, bv, lipschitz) for hw before this 
  lab('drawing-width',   'Drawing Gaussian Width'),
  lab('computing-width', 'Computing Gaussian Width'),
  review(),

  # Do Covering Numbers HW around now 
  lecture('covering-numbers', 'Bounding Gaussian Width using Covering Numbers'),
  lecture('chaining',         'Bounding Gaussian Width using Chaining'),
  lecture('curse',            'The Curse of Dimensionality'),
  lecture('non-gaussian',     'Least Squares and non-Gaussian Noise'),
  lecture('sampling',         'Least Squares, Sampling, and Population MSE'),
  review()
]
homeworks = {
  0: [homework('vector-spaces', 'Vector Spaces',                   due=datetime(2025, 1, 30))],
  1: [homework('inner-product-spaces', 'Inner Product Spaces',     due=datetime(2025, 1, 30))],
  2: [homework('smooth-regression', 'Option 1. Smooth Regression', due=datetime(2025, 2, 11)),
      homework('convex-regression', 'Option 2. Convex Regression', due=datetime(2025, 2, 11))],
  5: [homework('sobolev-models', 'Sobolev Models and Finite-Dimensional Approximation', due=datetime(2025, 2, 27))]
}
    
def censor(day, activity):
  endofclass = day.replace(hour=16, minute=15)
  if day >= sunday_of_week(datetime.now()) + relativedelta(weeks=1): 
    # if day is next week or later (i.e. after next sunday), no links
    return activity | {'href': None, 'notebook': None, 'html': None, 'solution-href': None, 'solution-notebook': None, 'solution-html': None}
  elif endofclass >= datetime.now():
    # if it's before end of class on day, no solution links
    return activity | {'solution-href': None, 'solution-notebook': None, 'solution-html': None}
  else:
    # if it's after end of class on day, show links
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
partials = {x : compiler.compile(open(f"templates/{x}.mustache", "r").read()) for x in ['lecture', 'homework', 'lab', 'review', 'dayoff', 'notebook', 'solution-notebook']}
output = template( {'weeks' : weeks }, partials=partials)
open('_site/index.html', 'w').write(output)
