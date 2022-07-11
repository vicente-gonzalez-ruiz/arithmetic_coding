include $(HOME)/LaTeX_templates/Makefile

arithmetic_coding.py:	arithmetic_coding.ipynb
			jupyter nbconvert --to script arithmetic_coding.ipynb

test:	arithmetic_coding.py
	ipython arithmetic_coding.py

default:	index.html test
