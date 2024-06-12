import src.dataset.amlsim.loader as amlsim_loader
import src.dataset.amlsim.amlsim_1m_preprocess as amlsim_preprocess
import src.dataset.itaml.loader as itaml_loader
import src.dataset.itaml.itaml_preprocess as itaml_preprocess
import src.dataset.berka.loader as berka_loader
import src.dataset.rabo.loader as rabo_loader

def main():
    print('Reformatting Berka')
    berka_loader.main()
    print('Reformatting AMLSim')
    amlsim_preprocess.main()
    amlsim_loader.main()
    print('Reformatting IT-AML')
    itaml_preprocess.main()
    itaml_loader.main()
    print('Reformatting Rabobank')
    rabo_loader.main()

if __name__ == '__main__':
    main()