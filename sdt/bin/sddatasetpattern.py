#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

##################################
#  @program        synda
#  @description    climate models data transfer program
#  @copyright      Copyright “(c)2009 Centre National de la Recherche Scientifique CNRS. 
#                             All Rights Reserved”
#  @license        CeCILL (https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/LICENSE)
##################################

"""This module contains dataset pattern utils."""

import argparse
import sdapp
import sddatasetdao
import sdproduct
from sddatasetversion import DatasetVersions
from sdtypes import Dataset
from sdtools import print_stderr
from sdexception import SDException

def build_dataset(dataset_pattern):
    d=Dataset()
    d.dataset_pattern=dataset_pattern

    # explode dataset_pattern to o1/o2
    (local_path_output1,local_path_output2)=sdproduct.get_output12_dataset_paths(dataset_pattern)

    # retrieve dataset from db
    d1=sddatasetdao.get_dataset_(local_path=local_path_output1)
    d2=sddatasetdao.get_dataset_(local_path=local_path_output2)

    if d1 and d2:

        # do some consistency checks between output1 dataset and output2 dataset

        if d1.latest != d2.latest:
            print_stderr('Inconsistency detected: latest flag differ between %s and %s'%(d1.local_path,d2.local_path))

        if d1.timestamp != d2.timestamp:
            print_stderr('Inconsistency detected: timestamp differ between %s and %s'%(d1.local_path,d2.local_path))

    elif d1:
        d.version=d2.version
        d.timestamp=d2.timestamp
    elif d2:
        d.version=d2.version
        d.timestamp=d2.timestamp
    else:
        raise SDException()

    return d

def check_requirement(dataset_pattern_paths):
    assert len(dataset)==2
    assert 'CMIP5' in path for path in dataset_pattern_paths

def build_datasetversions(dataset_pattern_paths):
    d1=build_dataset(dataset_pattern_paths[0])
    d2=build_dataset(dataset_pattern_paths[1])

    datasetVersions=DatasetVersions()
    datasetVersions.add_dataset_version(d1)
    datasetVersions.add_dataset_version(d2)

    return datasetVersions

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',nargs='?')
    parser.add_argument('dataset',nargs='*',default=[],help='Dataset pattern paths list')
    args = parser.parse_args()

    if args.action == 'latest':
        check_requirement(args.dataset)
        datasetVersions=build_datasetversions(args.dataset)
        print datasetVersions.get_latest_dataset().dataset_pattern
    elif args.action == 'oldest':
        check_requirement(args.dataset)
        datasetVersions=build_datasetversions(args.dataset)
        print datasetVersions.get_oldest_dataset().dataset_pattern
    else:
        print_stderr('Invalid operation %s'%args.action)   
