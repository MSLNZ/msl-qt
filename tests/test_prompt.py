from collections import OrderedDict

from msl.qt import prompt


def test_get_file_filters():
    assert 'All Files (*)' == prompt._get_file_filters(None)
    assert '' == prompt._get_file_filters('')
    assert '' == prompt._get_file_filters([])
    assert '' == prompt._get_file_filters({})

    assert 'Text files (*.txt)' == prompt._get_file_filters('Text files (*.txt)')
    assert 'Text files (*.txt)' == prompt._get_file_filters(['Text files (*.txt)'])
    assert 'Text files (*.txt)' == prompt._get_file_filters({'Text files': '*.txt'})
    assert 'Text files (*.txt)' == prompt._get_file_filters({'Text files': ('*.txt',)})
    assert 'Text files (*.txt)' == prompt._get_file_filters({'Text files': 'txt'})
    assert 'Text files (*.txt)' == prompt._get_file_filters({'Text files': '.txt'})
    assert 'Text files (test*.txt)' == prompt._get_file_filters({'Text files': 'test*.txt'})

    assert 'ABC files (abc*)' == prompt._get_file_filters('ABC files (abc*)')
    assert 'ABC files (abc*)' == prompt._get_file_filters({'ABC files': 'abc*'})

    assert 'Data files (*.txt *.xml *.csv my*.hdf5)' == prompt._get_file_filters({'Data files': ('txt', '.xml', '*.csv', 'my*.hdf5')})

    od = OrderedDict([('Data files', ('txt', 'ab*.xml', '*.csv', 'my*.hdf5')), ('XML files', 'xml')])
    assert 'Data files (*.txt ab*.xml *.csv my*.hdf5);;XML files (*.xml)' == prompt._get_file_filters(od)

    od = OrderedDict([('Data files', 'm*.xml'), ('All files', '*')])
    assert 'Data files (m*.xml);;All files (*)' == prompt._get_file_filters(od)

    assert 'Image files (*.png)' == prompt._get_file_filters('Image files (*.png);;')
    assert 'Image files (*.png *.jpg);;Text files (*.txt)' == prompt._get_file_filters('Image files (*.png *.jpg);;Text files (*.txt)')
    assert 'Image files (*.png *.jpg);;Text files (*.txt)' == prompt._get_file_filters(['Image files (*.png *.jpg)', 'Text files (*.txt)'])
    assert 'Image files (*.png *.jpg);;Text files (*.txt);;All Files (*)' == prompt._get_file_filters(['Image files (*.png *.jpg)', 'Text files (*.txt)', None])
