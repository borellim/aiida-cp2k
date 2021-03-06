# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
###############################################################################
# Copyright (c), The AiiDA-CP2K authors.                                      #
# SPDX-License-Identifier: MIT                                                #
# AiiDA-CP2K is hosted on GitHub at https://github.com/aiidateam/aiida-cp2k   #
# For further information on the license, see the LICENSE.txt file.           #
###############################################################################
"""Run simple DFT calculation"""

from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import ase.build
import click

from aiida.engine import run
from aiida.orm import (Code, Dict, SinglefileData, StructureData)
from aiida.common import NotExistent
from aiida.plugins import CalculationFactory

Cp2kCalculation = CalculationFactory('cp2k')


def example_structure_through_file(cp2k_code):
    """Run simple DFT calculation"""

    print("Testing CP2K ENERGY on H2O (DFT). Water molecule is provided through a file input...")

    pwd = os.path.dirname(os.path.realpath(__file__))

    # structure
    atoms = ase.build.molecule('H2O')
    atoms.center(vacuum=2.0)
    structure = StructureData(ase=atoms)

    # basis set
    basis_file = SinglefileData(file=os.path.join(pwd, "..", "files", "BASIS_MOLOPT"))

    # pseudopotentials
    pseudo_file = SinglefileData(file=os.path.join(pwd, "..", "files", "GTH_POTENTIALS"))

    # parameters
    parameters = Dict(
        dict={
            'FORCE_EVAL': {
                'METHOD': 'Quickstep',
                'DFT': {
                    'BASIS_SET_FILE_NAME': 'BASIS_MOLOPT',
                    'POTENTIAL_FILE_NAME': 'GTH_POTENTIALS',
                    'QS': {
                        'EPS_DEFAULT': 1.0e-12,
                        'WF_INTERPOLATION': 'ps',
                        'EXTRAPOLATION_ORDER': 3,
                    },
                    'MGRID': {
                        'NGRIDS': 4,
                        'CUTOFF': 280,
                        'REL_CUTOFF': 30,
                    },
                    'XC': {
                        'XC_FUNCTIONAL': {
                            '_': 'LDA',
                        },
                    },
                    'POISSON': {
                        'PERIODIC': 'none',
                        'PSOLVER': 'MT',
                    },
                },
                'SUBSYS': {
                    'TOPOLOGY': {
                        'COORD_FILE_NAME': 'water.xyz',
                        'COORD_FILE_FORMAT': 'XYZ'
                    },
                    'CELL': {
                        'ABC': '{:<15}  {:<15}  {:<15}'.format(*atoms.cell.diagonal()),
                    },
                    'KIND': [
                        {
                            '_': 'O',
                            'BASIS_SET': 'DZVP-MOLOPT-SR-GTH',
                            'POTENTIAL': 'GTH-LDA-q6'
                        },
                        {
                            '_': 'H',
                            'BASIS_SET': 'DZVP-MOLOPT-SR-GTH',
                            'POTENTIAL': 'GTH-LDA-q1'
                        },
                    ],
                },
            }
        })

    # Construct process builder
    builder = Cp2kCalculation.get_builder()
    builder.parameters = parameters
    builder.code = cp2k_code
    builder.file = {
        'basis': basis_file,
        'pseudo': pseudo_file,
        'water': structure,
    }
    builder.metadata.options.resources = {
        "num_machines": 1,
        "num_mpiprocs_per_machine": 1,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 3 * 60

    print("Submitted calculation...")
    run(builder)


@click.command('cli')
@click.argument('codelabel')
def cli(codelabel):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print("The code '{}' does not exist".format(codelabel))
        sys.exit(1)
    example_structure_through_file(code)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
