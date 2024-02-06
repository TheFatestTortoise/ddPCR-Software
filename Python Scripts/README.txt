Workflow:
csv3png -> dataAnnotation -> simpleViz -> DataAnalytics -> autoCut -> train-test-valSplit -> RUN YoloV5

csv3png:
	This uses a system of plotting smaller sections and then 	stitching them together
	These large images are useful for tagging since it can all 	be done in one push
	which is nice

	For inference save the temp images instead of the whole 	images

dataAnnotation:
	This code opens every image in the IMAGES directory to 	place boxes

	Currently this works with 4 classes:
  	  Rebound Peak - Right click
  	  Single Peak - Left click - Mode = 0
   	  Double Peak - Left click - Mode = 1
  	  And Poly Peak - Left click - Mode = 2
    
	saves txt files in relative form for YoloV5

simpleViz:
	Visualize relative pixel data on opencv2 screen
	No scroll bar only use for small images

autoCut:
	Splits files from a full sized file (upwards of 10000x470) 	into smaller chunks

	The chunks don't have bounding boxes on the edges and are 	autosized

train-test-valSplit:
	Splits data into train test and validation sets then moves 	them to the appropriate dataset

	THIS SCRIPT PERMANENTLY MOVES FILES FROM BOX_IN_DIR AND 	IMG_IN_DIR to val, test, train files

	Run autoSplit.py first to ensure there are files to move

	Advised to clear files from train, val, test directories