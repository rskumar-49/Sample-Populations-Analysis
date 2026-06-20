setup:
	python -m pip install -r requirements.txt

pipeline:
	python load_data.py
	python initial_analysis.py
	python stat_analysis.py
	python data_subset_analysis.py

dashboard:
	python make_visualization.py