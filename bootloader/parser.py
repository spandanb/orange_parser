import sys, os, pdb, argparse
from utils.io_utils import read_yaml, write_yaml, log, yaml_to_envvars
from utils.utils import create_and_raise

def bootload(template)
    topology = read_yaml(filepath=template)

def parse_args():
    parser = argparse.ArgumentParser(description='Bootloader command line interface')
    parser.add_argument('-f', '--template-file', nargs=1, help="specify the template to use")
    
    args = parser.parse_args()
    
    if args.template_file:
        bootload(args.template_file)

    else:
        parser.print_help()
        create_and_raise("TemplateNotSpecifiedException", "Please specify a template file")


if __name__ == "__main__":
    parse_args()
