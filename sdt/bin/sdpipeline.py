#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

##################################
#  @program        synda
#  @description    climate models data transfer program
#  @copyright      Copyright “(c)2009 Centre National de la Recherche Scientifique CNRS. 
#                             All Rights Reserved”
#  @license        CeCILL (https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/LICENSE)
##################################

"""This module contains small handy pipelines.

Note:
    Pipelines defined in this module are of higher level than those defined
    as standalone pipelines (pipelines defined in their own module), which 
    means that standalone pipelines can't use pipelines defined in this module.
"""

import json
import sdapp
import sdquerypipeline
import sdshrink
import sdparse
import sdbuffer
import sdparampipeline
import sdinference
import sdgenericpipeline
import sdfilepipeline
import sddatasetpipeline
import sddeferredafter
import sdlog
import sdconst
import sdpipelineprocessing
import sdexception

def post_pipeline_CHUNK_BY_CHUNK_OK(files,mode=None):

    assert isinstance(files,list)

    if mode=='file':
        files=sdgenericpipeline.run(files)
        files=sdfilepipeline.run(files=files)
    elif mode=='dataset':
        files=sdgenericpipeline.run(files)
        files=sddatasetpipeline.run(files=files)
    elif mode=='generic':
        files=sdgenericpipeline.run(files)
    elif mode is None:
        # if None, we return the result as is, any without transformation
        # (usefull for dumping malformed files JSON raw data, to make debugging malformed files more easy).

        pass
    else:
        raise sdexception.SDException("SDPIPELI-001","Incorrect mode (%s)"%mode)

    return files

def build_queries(stream=None,selection=None,path=None,parameter=None,index_host=None,load_default=None,query_type='remote',dry_run=False,parallel=True,count=False):
    """This pipeline add 'path', 'parameter' and 'selection' input type to the
    standalone query pipeline.

    Returns:
        squeries (Serialized queries) # TODO: maybe rename stream to dqueries
    """

    if parameter is None:
        parameter=[]

    if stream is None:

        if selection is None:
            buffer=sdbuffer.get_selection_file_buffer(path=path,parameter=parameter)
            selection=sdparse.build(buffer,load_default=load_default)

        stream=selection.merge_facets()


    # at this point, stream contains all possible parameters sources (file,stdin,cli..)


    if count:
        # in this mode, we don't want to return any files, so we force limit to
        # 0 just in case this option has been set by the user

        sddeferredafter.add_forced_parameter(stream,'limit','0')


    queries=sdquerypipeline.run(stream,index_host=index_host,query_type=query_type,dry_run=dry_run,parallel=parallel)
    return queries

def post_pipeline(metadata,mode=None):

    sdlog.info("SDPIPELI-004","Start main pipeline")

    metadata=sdpipelineprocessing.run_pipeline(sdconst.PROCESSING_FETCH_MODE_GENERATOR,metadata,post_pipeline_CHUNK_BY_CHUNK_OK,mode)

    sdlog.info("SDPIPELI-006","Main pipeline completed")

    if mode in ['file','dataset']:

        sdlog.info("SDPIPELI-002","Start shrink processing")
        metadata=sdshrink.run(metadata)
        sdlog.info("SDPIPELI-002","Shrink processing completed")

    return metadata

def prepare_param(selection=None,path=None,parameter=None,load_default=None):
    """This pipeline add 'path', 'parameter' and 'selection' input type to the
    standalone param pipeline."""

    if parameter is None:
        parameter=[]

    if selection is None:
        buffer=sdbuffer.get_selection_file_buffer(path=path,parameter=parameter)
        selection=sdparse.build(buffer,load_default=load_default)

    facets_groups=selection.merge_facets()

    facets_groups=sdparampipeline.run(facets_groups)

    return facets_groups

def parse(parameter=None):
    """This pipeline is used as a fast parameter parser (without further
    processing).
    """

    if parameter is None:
        parameter=[]

    buffer=sdbuffer.get_selection_file_buffer(parameter=parameter)
    selection=sdparse.build(buffer,load_default=False)
    facets_groups=selection.merge_facets()
    facets_groups=sdinference.run(facets_groups)
    return facets_groups
