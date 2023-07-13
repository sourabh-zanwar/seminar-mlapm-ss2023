# seminar-mlapm-ss2023
This is the repository for the code used for Replication and new methods implementaion for Seminar of MLAPM
In this repository I have changed the script type format of the original one, to a jupyter notebook for easier explainability and comprhensibility. The notebooks are namely:

1. ./prediction/Phase1.ipynb: 
		This notebook contains the phase one, along with the 4 models (LSTM, BiLSTM, GRU, CNN). These models need to be trained twice, once for *next_activity* and then for *processing_time*
2. ./Phase2_baseline.ipynb:
		No changes to this, I have only moved it to the notebook formate from script format.
3. ./Phase2_suggested.ipynb:
		In this the major changes are importing and using the new types of prediction models that we have used in this work. We need to change the name of the model in the class for changing the type of model used.

## How to run
1. Read the Readme_org file to check for the dependecnies and other information
2. Once the dependencies are installed, Open the *./prediction/Phase1.ipynb* notebook and run it for next_activity and processing_time. Change the name of the saved model as per the type of model used or as required.
3. Once the models are trained and saved, get the name of the models and pass them to the Phase 2.
4. Run Phase2_baseline.ipynb, it does not need any special instructions and is very straightforeard.
5. For Phase2_suggested.ipynb, one needs to change the model name/path based on which tyoe of model needs to be used. Specify experiment name for proper distinction between different experiments.
6. Steps 4 and 5 will generate a text file with their performance scores and save the file to the folder: *./exp_result/*.
7. Refer the files in *./exp_results/* folder for getting the Total Weighted Sum, Total Computation Time, Prediction Time and Optimization Time.
8. The files beginning with './exp_results/suggested*' are the ones using prediction based resource allocation.