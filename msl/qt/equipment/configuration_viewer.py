"""
A :class:`~QtWidgets.QWidget` to view the information within a
`Configuration File <http://msl-equipment.readthedocs.io/en/latest/config.html#configuration>`_.
"""
import re

try:
    from msl.equipment import Config, EquipmentRecord, ConnectionRecord
    has_msl_equipment = True
except ImportError:
    has_msl_equipment = False

from msl.qt import QtWidgets, QtCore
from msl.qt import prompt, Button, Logger
from msl.qt.io import get_drag_enter_paths
from msl.qt.equipment import show_record


class ConfigurationViewer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """A :class:`~QtWidgets.QWidget` to view a
        :ref:`Configuration File <msl.equipment:configuration_file>`.

        Parameters
        ----------
        parent : :class:`QtWidgets.QWidget`, optional
            The parent :class:`QtWidgets.QWidget`.

        Example
        -------
        To view an example of the :class:`ConfigurationViewer`, run:

        >>> from msl.examples.qt.equipment import configuration_viewer # doctest: +SKIP
        >>> configuration_viewer.show() # doctest: +SKIP
        """
        super(ConfigurationViewer, self).__init__(parent=parent)

        if not has_msl_equipment:
            raise ImportError('This class requires that MSL Equipment is installed')

        self.setAcceptDrops(True)
        self._dropped_path = None
        self._database = None

        #
        # selecting a configuration file
        #
        browse = Button(icon=QtWidgets.QStyle.SP_DialogOpenButton)
        browse.setToolTip('Select a configuration file')
        browse.set_left_click(self._browse_file)

        self._filebox = QtWidgets.QLineEdit()
        self._filebox.setToolTip('Drag \'n drop a configuration file')
        self._filebox.setReadOnly(True)

        select_layout = QtWidgets.QHBoxLayout()
        select_layout.addWidget(browse)
        select_layout.addWidget(self._filebox)
        select_layout.setSpacing(1)

        #
        # the filter field
        #
        self._filter = QtWidgets.QLineEdit()
        self._filter.setToolTip('Search filter for the database')
        self._filter.returnPressed.connect(self._apply_filter)

        filter_button = Button(icon=QtWidgets.QStyle.SP_FileDialogContentsView, tooltip='Apply filter')
        filter_button.set_left_click(self._apply_filter)

        clear_button = Button(icon=QtWidgets.QStyle.SP_LineEditClearButton, tooltip='Clear filter')
        clear_button.set_left_click(self._clear_filter)

        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(filter_button)
        filter_layout.addWidget(self._filter)
        filter_layout.addWidget(clear_button)
        filter_layout.setSpacing(1)

        #
        # the Tree and Tables
        #
        self._equipment_records_table = _RecordTable(EquipmentRecord, self)
        self._connection_records_table = _RecordTable(ConnectionRecord, self)
        self._equipment_table = _RecordTable(EquipmentRecord, self, is_dict=True)
        self._constants_table = _ConstantsTable(self)

        self._tree = _Tree(self._equipment_records_table, self._connection_records_table)
        self._tree.sig_selected.connect(self._tree_item_selected)
        self._tree.setToolTip('Double click an item to select it.\n\nHold the CTRL key to select multiple items.')

        tab = QtWidgets.QTabWidget()
        tab.addTab(self._equipment_records_table, 'Equipment Records')
        tab.addTab(self._connection_records_table, 'Connection Records')
        tab.addTab(self._equipment_table, 'Equipment Tags')
        tab.addTab(self._constants_table, 'Constants')
        tab.addTab(Logger(), 'Log')

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self._tree)
        splitter.addWidget(tab)
        splitter.setStretchFactor(1, 1)  # the tab expands to fill the full width
        splitter.setSizes((self._tree.sizeHint().width()*1.1, 1))

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(select_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

    def dragEnterEvent(self, event):
        """Overrides `dragEnterEvent <https://doc.qt.io/qt-5/qwidget.html#dragEnterEvent>`_."""
        paths = get_drag_enter_paths(event, pattern='*.xml')
        if paths:
            self._dropped_path = paths[0]
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Overrides `dropEvent <https://doc.qt.io/qt-5/qwidget.html#dropEvent>`_."""
        self._new_file(self._dropped_path)
        event.accept()

    def _browse_file(self):
        """Open a dialog to select a file"""
        path = prompt.filename(filters='Config (*.xml)')
        if path is not None:
            self._new_file(path)

    def _new_file(self, path):
        """Loads a new configuration file"""
        try:
            cfg = Config(path)
            database = cfg.database()
        except Exception as e:
            prompt.critical('Invalid configuration file\n\n{}'.format(e))
            return

        self._filebox.setText(path)
        self._equipment_records_table.set_database(database)
        self._connection_records_table.set_database(database)
        self._equipment_table.set_database(database)
        self._constants_table.update_table(cfg.root)
        self._tree.populate_tree()
        self._apply_filter()

    def _apply_filter(self):
        """Apply the filter"""
        if not self._filebox.text():
            prompt.warning('You have not loaded a configuration file')
        else:
            try:
                self._equipment_records_table.filter(self._filter.text())
                self._connection_records_table.filter(self._filter.text())
                self._equipment_table.filter(self._filter.text())
            except Exception as e:
                self._equipment_records_table.setRowCount(0)
                self._equipment_records_table.resizeColumnsToContents()
                self._connection_records_table.setRowCount(0)
                self._connection_records_table.resizeColumnsToContents()
                self._equipment_table.setRowCount(0)
                self._equipment_table.resizeColumnsToContents()
                prompt.critical(e.message)

    def _tree_item_selected(self, text):
        """An item in the Tree was double clicked"""
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier and self._filter.text():
            for entry in text.split(','):
                key, value = entry.split('=')
                if key in self._filter.text():
                    if value in self._filter.text():
                        continue
                    # take the logical OR with the new text
                    self._filter.setText(self._filter.text().replace(key+'=', '{}={}|'.format(key, value)))
                else:
                    # append the new text
                    self._filter.setText(self._filter.text() + ', {}={}'.format(key, value))
        else:
            self._filter.setText(text)
        self._apply_filter()

    def _clear_filter(self):
        """Clear the filter text"""
        self._filter.setText('')
        if self._filebox.text():
            self._apply_filter()


class _RecordTable(QtWidgets.QTableWidget):

    allowed_keys = ['year_calibrated']  # contains the key names for both Equipment and Connection Record's

    def __init__(self, record_type, parent, is_dict=False):
        super(_RecordTable, self).__init__(parent)

        self._database = None

        self._is_equipment_record = record_type is EquipmentRecord
        self._is_dict = is_dict
        self._keys = record_type().to_dict().keys()
        for k in self._keys:
            if k not in self.allowed_keys:
                self.allowed_keys.append(k)

        self.records_all = None

        self.header = [h.replace('_', ' ').title() for h in sorted(self._keys)]
        self.setColumnCount(len(self.header))
        self.setHorizontalHeaderLabels(self.header)
        self.setSortingEnabled(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # disable editing the table
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # highlight entire row when selected
        self.horizontalHeader().setStretchLastSection(True)  # make the last column stretch to fill the table
        self.resizeColumnsToContents()

        self.cellDoubleClicked.connect(self.show_summary)

    def set_database(self, database):
        self._database = database
        if self._is_dict:
            self.records_all = database.equipment.values()
        else:
            if self._is_equipment_record:
                self.records_all = database.records()
            else:
                self.records_all = database.connections()
        self.filter('')

    def get_records(self, text=''):
        kwargs = {}
        search_for_raw_strings = []

        # for date_calibrated a test for equality could be used in the lambda function
        # don't want to split the text filter based on the '==' string
        text = text.replace('==', '::')
        for item in re.split(',', text, flags=re.IGNORECASE):
            kv = re.split('=', item)
            if not kv[0]:
                continue
            if len(kv) == 1:
                search_for_raw_strings.append(kv[0])
                continue

            key = kv[0].strip()
            value = kv[1].strip().replace('::', '==')
            if key == 'year_calibrated':
                key = 'date_calibrated'
                val = 'lambda date: '
                for year in value.split('|'):
                    val += 'date.year == {} or '.format(year)
                value = eval(val[:-4])
            else:
                try:
                    value = eval(value)  # assume that the input can be trusted so that eval() is okay to use
                except Exception as e:
                    pass

            if key not in self.allowed_keys:
                raise KeyError('Invalid filter name "{}"'.format(key))

            if key in self._keys:
                kwargs[key] = value
            else:
                return []

        records = [r for r in self.records_all if self._database._search(r, kwargs, 0)]

        for item in search_for_raw_strings:
            for record in self.search_database_for_string(item):
                if record not in records:
                    records.append(record)

        return records

    def search_database_for_string(self, text):
        records = []
        text_split = [item.strip() for item in text.lower().split(',') if item.strip()]
        for record in self.records_all:
            string = record.to_yaml().lower()
            for item in text_split:
                if item in string:
                    records.append(record)
                    break
        return records

    def filter(self, text):
        self.setRowCount(0)
        self.resizeColumnsToContents()

        text = text.strip()
        if not text:
            records = self.records_all
        elif '=' not in text:
            records = self.search_database_for_string(text)
        else:
            records = self.get_records(text)

        if not records:
            return

        self.setRowCount(len(records))
        for row, record in enumerate(records):
            for col, element in enumerate(record.to_xml()):
                if element.tag == 'connection' and record.connection is not None:
                    self.setItem(row, col, QtWidgets.QTableWidgetItem('True'))
                elif element.tag == 'properties':
                    text = u''
                    if not element:
                        self.setItem(row, col, QtWidgets.QTableWidgetItem(text))
                    else:
                        for sub_element in element:
                            text += u'{}={}; '.format(sub_element.tag, sub_element.text)
                            self.setItem(row, col, QtWidgets.QTableWidgetItem(text))
                else:
                    self.setItem(row, col, QtWidgets.QTableWidgetItem(element.text))
        self.resizeColumnsToContents()

    def show_summary(self, row, column):
        # find the record
        search = {}
        for c in range(self.columnCount()):
            search[self.header[c].lower().replace(' ', '_')] = self.item(row, c).text()
        for record in self.records_all:
            found_record = True
            for element in record.to_xml():
                if element.text and search[element.tag] and search[element.tag] != element.text:
                    found_record = False
                    break
            if found_record:
                break
        show_record(record)


class _Tree(QtWidgets.QTreeWidget):

    sig_selected = QtCore.pyqtSignal(str)

    def __init__(self, equipment_table, connection_table):
        """A Tree view of the options to use as filters for the devices."""
        super(_Tree, self).__init__()

        # configure the super class
        self.setColumnCount(1)
        self.header().close()
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.itemDoubleClicked.connect(self._item_clicked)

        self.equipment_table = equipment_table
        self.connection_table = connection_table
        self.skip_names = ('Alias', 'Asset Number', 'Description', 'Latest Report Number', 'Model', 'Serial')
        self.rename_map = {'Date Calibrated': 'Year Calibrated'}
        self.create_top_level()

    def create_top_level(self):
        top_level_names = []
        for name in self.equipment_table.header:
            if name in self.skip_names:
                continue
            if name in self.rename_map:
                name = self.rename_map[name]
            top_level_names.append(name)

        top_level_names.extend(['Backend', 'Interface'])  # for ConnectionRecord's

        for item in sorted(top_level_names):
            QtWidgets.QTreeWidgetItem(self, [item])

    def populate_tree(self):
        self.clear()
        self.create_top_level()

        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            name = item.text(0)
            if name == 'Manufacturer':
                values = {}
                for record in self.equipment_table.records_all:
                    if record.manufacturer and record.manufacturer not in values:
                        values[record.manufacturer] = [record.model]
                    else:
                        if record.model and record.model not in values[record.manufacturer]:
                            values[record.manufacturer].append(record.model)
                item.setText(0, name + ' ({})'.format(len(values)))
                for manufacturer in sorted(values):
                    model_item = QtWidgets.QTreeWidgetItem(item, [manufacturer])
                    for model in sorted(values[manufacturer]):
                        QtWidgets.QTreeWidgetItem(model_item, [model])
            elif name == 'Year Calibrated':
                years = []
                for record in self.equipment_table.records_all:
                    year = record.date_calibrated.year
                    if year > 1 and year not in years:
                        years.append(year)
                item.setText(0, name + ' ({})'.format(len(years)))
                for year in sorted(years)[::-1]:
                    QtWidgets.QTreeWidgetItem(item, [str(year)])
            elif name == 'Connection':
                bools = {'True': 0, 'False': 0}
                for record in self.equipment_table.records_all:
                    bools[str(record.connection is not None)] += 1
                item.setText(0, name + ' (2)')
                for key in sorted(bools):
                    QtWidgets.QTreeWidgetItem(item, [key])
            elif name == 'Calibration Cycle':
                cycles = []
                for record in self.equipment_table.records_all:
                    if record.calibration_cycle == 0:
                        continue
                    if int(record.calibration_cycle) == record.calibration_cycle:
                        cycle = int(record.calibration_cycle)
                    else:
                        cycle = record.calibration_cycle
                    if cycle not in cycles:
                        cycles.append(cycle)
                item.setText(0, name + ' ({})'.format(len(cycles)))
                for c in sorted(cycles):
                    QtWidgets.QTreeWidgetItem(item, [str(c)])
            else:
                if name == 'Backend' or name == 'Interface':
                    values = self._get_distinct_connection_records(name)
                else:
                    values = self._get_distinct_equipment_records(name)
                item.setText(0, name + ' ({})'.format(len(values)))
                for value in sorted(values):
                    QtWidgets.QTreeWidgetItem(item, [value])

    def _get_distinct_equipment_records(self, name):
        out = []
        attrib = name.lower().replace(' ', '_')
        for record in self.equipment_table.records_all:
            value = u'{}'.format(getattr(record, attrib))
            if value and value not in out:
                out.append(value)
        return out

    def _get_distinct_connection_records(self, name):
        out = []
        attrib = name.lower().replace(' ', '_')
        for record in self.connection_table.records_all:
            value = getattr(record, attrib).name
            if value and value not in out:
                out.append(value)
        return out

    def _item_clicked(self, item, column):
        num_parents = 0
        parent = item.parent()
        while parent is not None:
            parent = parent.parent()
            num_parents += 1

        if num_parents == 0:  # then a top-level item was clicked
            return

        if num_parents == 1:
            attrib_name = item.parent().text(column).split(' (')[column].lower().replace(' ', '_')
            text = u'{}={}'.format(attrib_name, item.text(column))
        else:
            attrib_name = item.parent().parent().text(column).split(' (')[column].lower().replace(' ', '_')
            text = u'{}={}, model={}'.format(attrib_name, item.parent().text(column), item.text(column))

        self.sig_selected.emit(text)


class _ConstantsTable(QtWidgets.QTableWidget):

    def __init__(self, parent):
        super(_ConstantsTable, self).__init__(parent)

        self._database = None

        self.header = ['Key', 'Value', 'Attributes']
        self.setColumnCount(len(self.header))
        self.setHorizontalHeaderLabels(self.header)
        self.setSortingEnabled(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # disable editing the table
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # highlight entire row when selected
        self.horizontalHeader().setStretchLastSection(True)  # make the last column stretch to fill the table
        self.resizeColumnsToContents()

    def update_table(self, root):
        items = [(e.tag, e.text, e.attrib) for e in root if not e.tag.startswith('equipment')]
        self.setRowCount(len(items))
        for i, item in enumerate(items):
            self.setItem(i, 0, QtWidgets.QTableWidgetItem(item[0]))
            self.setItem(i, 1, QtWidgets.QTableWidgetItem(item[1]))
            text = '; '.join('{}={}'.format(k, v) for k, v in item[2].items())
            self.setItem(i, 2, QtWidgets.QTableWidgetItem(text))
        self.resizeColumnsToContents()
