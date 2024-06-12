from src.experiments.timestamp_analysis.itaml import timestamp_plots as itaml_timestamp_plots
from src.experiments.timestamp_analysis.amlsim import timestamp_plots as amlsim_timestamp_plots

def main():
    print('Analyzing AMLSim timestamps')
    amlsim_timestamp_plots.main()
    print('Analyzing ITAML timestamps')
    itaml_timestamp_plots.main()

if __name__ == '__main__':
    main()