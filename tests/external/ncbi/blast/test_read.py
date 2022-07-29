import pytest

from topiary.external.ncbi.blast.read import _xml_file_to_records
from topiary.external.ncbi.blast.read import records_to_df
from topiary.external.ncbi.blast.read import read_blast_xml

import os, shutil

def test__xml_file_to_records(user_xml_files):

    # Basically wrapper for biopython reader. Make sure it reads some real
    # files, including one with CREATE_VIEW nastiness
    for f in user_xml_files:

        out = _xml_file_to_records(f)
        expected_length = user_xml_files[f]["length"]
        expected_queries = user_xml_files[f]["queries"]
        assert len(out) == expected_queries

        # length is for first query
        for o in out[:1]:
            assert len(list(o.alignments)) == expected_length

def test_records_to_df(user_xml_files):

    for f in user_xml_files:

        xml_records = _xml_file_to_records(f)
        expected_length = user_xml_files[f]["length"]
        expected_queries = user_xml_files[f]["queries"]

        df = records_to_df(xml_records)

        # Hack, really. If there is only one query, make sure the dataframe
        # has expected length. If more than one, make sure dataframe is longer.
        # (To implement correctly -- passing full length -- I'd have to
        # refactor conftest entry. Maybe later)
        if expected_queries == 1:
            assert len(df) == expected_length
        else:
            assert len(df) > expected_length

def test_read_blast_xml(xml,tmpdir,user_xml_files):

    # Pass in a single xml file, not in a list
    xml_file = xml["good.xml"]
    df, xml_files = read_blast_xml(xml_file)
    assert isinstance(df,list)
    assert isinstance(xml_files,list)
    assert len(df) == 1
    assert len(xml_files) == 1
    assert len(df[0]) == 19
    assert xml_files[0] == xml_file

    # Pass two xml files
    df, xml_files = read_blast_xml([xml_file,xml_file])
    assert isinstance(df,list)
    assert isinstance(xml_files,list)
    assert len(df) == 2
    assert len(xml_files) == 2
    assert len(df[0]) == 19
    assert len(df[1]) == 19
    assert xml_files[0] == xml_file
    assert xml_files[1] == xml_file

    # Pass directory with an xml file
    xml_files_dir = os.path.join(tmpdir,"xml_files")
    os.mkdir(xml_files_dir)
    shutil.copy(xml_file,
                os.path.join(xml_files_dir,os.path.split(xml_file)[-1]))
    df, xml_files = read_blast_xml(xml_files_dir)

    assert len(df) == 1
    assert len(xml_files) == 1
    assert len(df[0]) == 19
    assert xml_files[0] == os.path.join(xml_files_dir,os.path.split(xml_file)[-1])

    # Make directory with no xml files. Should die.
    no_xml_files_dir = os.path.join(tmpdir,"no_xml_files")
    os.mkdir(no_xml_files_dir)
    with pytest.raises(ValueError):
        df, xml_files = read_blast_xml(no_xml_files_dir)

    # Passing a stupid xml file with broken format ... not a great test, but
    # should at least throw error of some sort.
    xml_file = xml["bad.xml"]
    with pytest.raises(ValueError):
        df, xml_files = read_blast_xml(xml_file)

    # Test read of some basic examples
    df, xml_files = read_blast_xml(user_xml_files)
    assert len(df) == len(user_xml_files)
