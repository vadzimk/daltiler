import json
import math
import time
import traceback
from PySide2 import QtGui
from PySide2.QtCore import Slot, QRegExp, QObject, Signal, QThread, Qt
from PySide2.QtGui import QPalette, QColor, QRegExpValidator
from PySide2.QtWidgets import *
from UI_MainWindow import Ui_MainWindow
from modules2.PdfDoc import PdfDoc
from modules2.func import *
from modules2.tf import create_target_and_uom


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setFixedSize(679, 430)
        self.setWindowTitle("Daltiler")
        self.help_action = QAction(self, text="Help")
        self.about_action = QAction(self, text="About")
        help_text = "<h4>Before running `Daltiler`</h4>" \
                    "<ul>" \
                    "<li>export tabula-template.json of the pdf catalog with the help of <a href='https://tabula.technology'>Tabula for Windows</a></li>" \
                    "<li>Use autodetect tables to create tabula-template.json</li>" \
                    "</ul>"
        about_text = "<h4>`Daltiler` automates data entry into the ERP system from pdf catalogue of one specific vendor</h4><h5>Input:</h5>" \
                     "<ul>" \
                     "<li>pdf file containing pages with tables from Daltile catalog</li>" \
                     "<li>tabula-template.json file</li>" \
                     "</ul>" \
                     "<h5>Output</h5>" \
                     "<ul>" \
                     "<li>product_table.csv - structured data extracted from all fields of tables</li>" \
                     "<li>target.csv - client's template for upload in ERP</li>" \
                     "<li>uom.csv - another client's template containing units conversion for upload in ERP</li>" \
                     "</ul>" \
                     "<a href='mailto:vadzimk@hotmail.com'>Email developer</a>"
        self.help_action.triggered.connect(lambda: self.show_help_text(help_text))
        self.about_action.triggered.connect(lambda: self.show_help_text(about_text))
        self.menubar.addAction(self.help_action)
        self.menubar.addAction(self.about_action)

        self.progressBar.setVisible(False)

        self.pushButton.setEnabled(False)
        self.pushButton_5.setVisible(False)
        self.connect_signals_and_slots()

        # Worker args
        self.infilename = None
        self.template_filename = None
        self.page_start = None
        self.page_end = None
        self.output_path = None
        self.product_table_path = None
        #  end Worker args

        self.infilename_n_pages = None
        self.pushButton.setText("Start")
        self.errors = []
        self.thread = None
        self.worker = None
        self.initialize_fields()
        self.start_time = None

    def show_help_text(self, text):
        msg_box = QMessageBox()
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(text)
        msg_box.setWindowFlags(self.windowFlags() | Qt.Popup)
        msg_box.exec_()

    # for debugging
    def initialize_fields(self):
        self.lineEdit.setText("D:/Tileshop/daltiler/n.pdf")
        self.lineEdit_4.setText("D:/Tileshop/daltiler/n.tabula-template.json")
        self.lineEdit_2.setText("5")
        self.lineEdit_3.setText("191")
        self.lineEdit_9.setText("D:/Tileshop/daltiler/project_daltiler")

    def connect_signals_and_slots(self):
        self.pushButton_3.clicked.connect(self.select_infilename)
        self.lineEdit.textChanged.connect(self.handle_edit_infilename)
        self.lineEdit.editingFinished.connect(self.handle_number_of_pages)

        self.pushButton_2.clicked.connect(self.select_template_filename)
        self.lineEdit_4.textChanged.connect(self.handle_edit_template_filename)
        self.pushButton_4.clicked.connect(self.reset_all)
        self.pushButton.clicked.connect(self.handle_run)
        int_sting_validator = QRegExpValidator(QRegExp(r'^[1-9][0-9]+$'), self)
        self.lineEdit_2.setValidator(int_sting_validator)
        self.lineEdit_2.textChanged.connect(self.set_page_start)

        self.lineEdit_3.setValidator(int_sting_validator)
        self.lineEdit_3.textChanged.connect(self.set_page_end)

        self.pushButton_7.clicked.connect(self.select_output_path)
        self.lineEdit_9.textChanged.connect(self.handle_edit_output_path)

    @Slot(None)
    def open_file(self, path):
        print(path)
        try:
            os.startfile(path)
        except PermissionError:
            msg = f"{os.path.basename(path)}\nAccess denied"
            self.show_error_dialog(msg)

    @Slot(None)
    def reset_all(self):
        self.lineEdit.setText("")
        self.lineEdit_4.setText("")
        self.lineEdit_2.setText("")
        self.lineEdit_3.setText("")
        self.lineEdit_9.setText("")
        self.label.setText("/")
        self.label_3.setText("/")

        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        self.statusbar.clearMessage()
        self.pushButton_5.setVisible(False)
        self.enable_line_edits_and_selects(True)
        try:
            self.pushButton.clicked.disconnect()
        except Exception:
            pass
        self.pushButton.clicked.connect(self.handle_run)

    @Slot(None)
    def select_output_path(self):
        self.output_path = QFileDialog.getExistingDirectory(self, "Open Directory",
                                                            "./",
                                                            QFileDialog.ShowDirsOnly
                                                            | QFileDialog.DontResolveSymlinks)
        self.lineEdit_9.setText(self.output_path)
        self.handle_background(self.lineEdit_9, is_valid=True)
        self.set_start_enabled()

    @Slot(str)
    def handle_edit_output_path(self, text):
        is_path_valid = True
        if text:
            self.output_path = text
            is_path_valid = text and os.path.exists(text) and os.path.isdir(text)
        else:
            self.output_path = None
        self.handle_background(self.lineEdit_9, is_valid=is_path_valid)
        self.set_start_enabled(is_path_valid)

    @Slot(str)
    def set_page_end(self, text):
        if text:
            self.page_end = int(text)
            self.set_start_enabled()
        else:
            self.page_end = None

    @Slot(str)
    def set_page_start(self, text):
        if text:
            self.page_start = int(text)
            self.set_start_enabled()
        else:
            self.page_start = None

    @Slot(None)
    def handle_number_of_pages(self):
        if self.infilename:
            try:
                self.infilename_n_pages = get_pdf_page_count(self.infilename)
                self.label.setText("/" + str(self.infilename_n_pages))
                self.label_3.setText("/" + str(self.infilename_n_pages))
            except FileNotFoundError:
                self.label.setText("/")
                self.label_3.setText("/")

    @staticmethod
    def handle_background(line_edit_obj, is_valid):
        palette = QPalette()
        if not is_valid:
            palette.setColor(QPalette.Base, QColor(255, 0, 0, 127))
            line_edit_obj.setPalette(palette)
        else:
            palette.setColor(QPalette.Base, QColor(255, 255, 255, 255))
            line_edit_obj.setPalette(palette)

    @Slot(None)
    def select_infilename(self):
        self.infilename, _ = QFileDialog.getOpenFileName(self, "Open PDF", dir="./",
                                                         filter="Pdf (*.pdf);; All files (*.*)")
        self.lineEdit.setText(self.infilename)
        self.handle_background(self.lineEdit, is_valid=True)
        self.handle_number_of_pages()
        self.set_start_enabled()

    @Slot(str)
    def handle_edit_infilename(self, text):
        is_path_valid = True
        if text:
            self.infilename = text
            is_path_valid = text and os.path.exists(text) and os.path.isfile(text)
        else:
            self.infilename = None
        self.handle_background(self.lineEdit, is_valid=is_path_valid)
        self.set_start_enabled(is_path_valid)

    @Slot(None)
    def select_template_filename(self):
        self.template_filename, _ = QFileDialog.getOpenFileName(self, "Open tabula-template.json", dir="./",
                                                                filter="JSON (*tabula-template.json);; All files (*.*)")
        self.lineEdit_4.setText(self.template_filename)
        self.handle_background(self.lineEdit_4, is_valid=True)
        self.set_start_enabled(True)

    def is_valid_template_file(self, path):
        with open(path) as template_file:
            data = json.load(template_file)
            page_map = {p: False for p in range(self.page_start, self.page_end + 1)}
            for item in data:
                if item["page"] in range(self.page_start, self.page_end + 1):
                    page_map[item["page"]] = True
            isvalid = False not in page_map.values()
            if not isvalid:
                # print("page_map", page_map)
                missing_pages_in_json = [str(k) for k, v in page_map.items() if v == False]
                missing_pages_in_json_str = ', '.join(missing_pages_in_json)
                err_msg = f"{os.path.basename(self.template_filename)}\nmissing selections from pages: {missing_pages_in_json_str}"
                self.errors.append(err_msg)

        return isvalid

    @Slot(str)
    def handle_edit_template_filename(self, text):
        is_path_valid = True
        if text:
            self.template_filename = text
            is_path_valid = text and os.path.exists(text) and os.path.isfile(text)
        else:
            self.template_filename = None
        self.handle_background(self.lineEdit_4, is_valid=is_path_valid)
        self.set_start_enabled()

    def set_start_enabled(self, is_valid=True):
        ready = bool(
            is_valid and
            self.infilename and
            self.template_filename and
            self.output_path and
            self.page_start and
            self.page_end

        )
        self.pushButton.setEnabled(ready)
        return ready

    def check_input(self):
        ready = bool(
            self.file_exists(self.infilename) and
            self.file_exists(self.template_filename) and
            self.page_start_end_in_range() and
            self.is_valid_template_file(self.template_filename) and
            self.file_exists(self.output_path, "dir") and
            self.file_writable(self.output_path)

        )
        if not ready:
            text = "\n".join(self.errors)
            self.show_error_dialog(text)

        return ready

    @staticmethod
    def file_writable(path):
        access = os.access(path, os.W_OK)
        return access

    @staticmethod
    def file_exists(path, file_type="file"):
        is_type = os.path.isfile
        if file_type == "dir":
            is_type = os.path.isdir
        if not os.path.exists(path) or not is_type(path):
            return False
        return True

    def page_start_end_in_range(self):
        if self.page_start and self.page_end and self.infilename_n_pages and not (
                self.page_start <= self.page_end <= self.infilename_n_pages):
            err_msg = "Selected pages are out of range"
            self.errors.append(err_msg)
            return False
        return True

    def enable_line_edits_and_selects(self, value):
        self.lineEdit.setEnabled(value)
        self.lineEdit_2.setEnabled(value)
        self.lineEdit_9.setEnabled(value)
        self.lineEdit_4.setEnabled(value)
        self.lineEdit_3.setEnabled(value)
        self.pushButton_3.setEnabled(value)
        self.pushButton_2.setEnabled(value)
        self.pushButton_7.setEnabled(value)

    def set_page_progress(self, p):
        # print(f"pages processed {p}")
        progress = int(math.ceil(p * 100 / (self.page_end - self.page_start + 1)))
        self.progressBar.setValue(min(progress, 99))
        duration = time.time() - self.start_time
        estimated_sec_remaining = 100 * duration / progress - duration
        minutes, seconds = divmod(estimated_sec_remaining, 60)
        self.statusbar.showMessage(f"N pages read: {p}. Remaining time: {int(minutes)}min {int(seconds)}sec.")
        # print('progress', self.progressBar.value())

    def show_info_dialog(self, text):
        QMessageBox.information(self, "Info", text, QMessageBox.StandardButton.Ok)

    def show_error_dialog(self, text):
        ret = QMessageBox.warning(self, "Error", text, QMessageBox.StandardButton.Ok)
        if ret:
            self.errors = []

    def on_product_table_exported(self, time_msg):
        self.statusbar.showMessage(time_msg)

        self.show_info_dialog("Product table created!\nYou may edit it before continuing")
        # change ui to Continue
        self.enable_line_edits_and_selects(False)
        self.pushButton.setText("Continue")
        self.pushButton.setEnabled(True)
        self.statusbar.showMessage("Press Continue to create target.csv, uom.csv")
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.setText(f"Open product table")
        self.pushButton_5.setVisible(True)
        try:
            self.pushButton_5.clicked.disconnect()
        except Exception:
            pass
        self.pushButton_5.clicked.connect(lambda: self.open_file(f"{self.output_path}/product_table.csv"))

    def on_permission_error(self):
        self.pushButton.setText("Continue")
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(False)

    def on_finished_success(self):
        self.statusbar.clearMessage()
        self.progressBar.setValue(100)
        self.show_info_dialog("Output files created!")
        # Change ui to done
        self.pushButton_4.setEnabled(True)
        self.pushButton.setText("Start")
        self.pushButton.setEnabled(False)
        self.pushButton_5.setVisible(True)
        self.pushButton_5.setText("Open output folder")
        try:
            self.pushButton_5.clicked.disconnect()
        except Exception:
            pass
        self.pushButton_5.clicked.connect(lambda: self.open_file(self.output_path))

        self.statusbar.showMessage("Done")
        self.enable_line_edits_and_selects(False)

    def set_start_time(self, start_time):
        self.start_time = start_time

    @Slot(None)
    def on_restart(self):
        try:
            self.pushButton.clicked.disconnect()
        except Exception:
            pass
        self.pushButton.clicked.connect(self.handle_run)
        self.pushButton.setText("Start")
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        # self.worker.deleteLater()
        # self.thread.deleteLater()
        # self.thread.quit()
        self.progressBar.setVisible(False)
        self.enable_line_edits_and_selects(True)

    @Slot(None)
    def handle_run(self):
        ready = self.set_start_enabled() and self.check_input()
        if not ready:
            return
        # Prepare ui to run
        # print("handle run entered")
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        self.pushButton_4.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(lambda: self.worker.run())  # btn re-enters run
        self.enable_line_edits_and_selects(False)

        args = {
            "infilename": self.infilename,
            "template_filename": self.template_filename,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "output_path": self.output_path,
            "product_table_path": self.product_table_path
        }

        self.thread = QThread()
        self.worker = Worker(**args)
        # print("Background Worker thread created")
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.started.connect(self.set_start_time)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.worker.progress.connect(self.set_page_progress)
        self.worker.error.connect(self.show_error_dialog)
        self.worker.restart.connect(self.on_restart)
        self.worker.product_table_exported.connect(self.on_product_table_exported)
        self.worker.status.connect(lambda msg: self.statusbar.showMessage(msg))
        self.worker.permission_error.connect(self.on_permission_error)
        self.worker.finished_success.connect(self.on_finished_success)
        self.thread.start()
        # print("Background Worker thread started")


class Worker(QObject):
    # class attributes
    started = Signal(int)
    finished = Signal()
    progress = Signal(int)
    error = Signal(str)
    restart = Signal()
    product_table_exported = Signal(str)
    permission_error = Signal()
    status = Signal()
    finished_success = Signal()

    # * parameter signifies no positional arg is allowed after *, only keyword args
    def __init__(self, *, infilename, template_filename, page_start, page_end, output_path, product_table_path):
        super(Worker, self).__init__()
        self.infilename = infilename
        self.template_filename = template_filename
        self.page_start = page_start
        self.page_end = page_end
        self.output_path = output_path
        self.product_table_path = product_table_path

        self.coro = self.run_generator()

    def run(self):
        try:
            next(self.coro)
        except StopIteration:
            self.finished.emit()
            return

    def run_generator(self):
        start_time = time.time()
        self.started.emit(start_time)
        # print(f"run generator entered")

        price_list = PdfDoc(
            in_file_name=self.infilename,
            template_json=self.template_filename,
            page_start=self.page_start,
            n_pages=self.page_end - self.page_start + 1,
        )

        # print("doc obj created")

        try:
            # for single-threaded call:
            # price_list.create_pages(callback=lambda p: self.progress.emit(p-self.page_start+1))
            price_list.create_pages_in_threads(callback=lambda p: self.progress.emit(p), n_threads=1)
            # print("pages created")
        except Exception:
            err_msg = f"Could not complete task!\nPossible errors:\n{os.path.basename(self.template_filename)} doesn't contain required tables\nor\n{os.path.basename(self.infilename)} layout not supported"
            print(err_msg)
            self.error.emit(err_msg)
            traceback.print_exc()
            self.restart.emit()
            return

        price_list.create_product_tables()
        price_list.construct_cumulative_dict()
        price_list.patch_cumulative_dictionary()

        product_table_path = f'{self.output_path}/product_table.csv'
        product_table_export_success = False
        while not product_table_export_success:
            try:
                product_table_export_success = price_list.export_cumulative_dict(product_table_path)
            except PermissionError:
                # signal ui of error in product table access
                err_msg = f"{os.path.basename(self.product_table_path)}\nAccess denied. Close applications that might use it and press Continue"
                self.error.emit(err_msg)
                self.status.emit(err_msg)
                self.permission_error.emit()
                yield

        end_time = time.time()
        hours, rem = divmod(end_time - start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        time_msg = f"Time elapsed: {minutes:.0f} min {seconds:.0f} sec\n"
        self.product_table_exported.emit(time_msg)
        yield

        # continuing
        target_uom_export_success = False
        while not target_uom_export_success:
            try:
                target_uom_export_success = create_target_and_uom(
                    f'{self.output_path}/product_table.csv',
                    f'{self.output_path}/target.csv',
                    f'{self.output_path}/uom.csv'
                )
            except PermissionError:
                err_msg = f"target.csv or uom.csv\nAccess denied. Close applications that might use it and press Continue"
                self.error.emit(err_msg)
                self.status.emit(err_msg)
                self.permission_error.emit()
                yield
        self.finished_success.emit()
        return


def main():
    app = QApplication([])
    app.setWindowIcon(QtGui.QIcon('Dv2.ico'))
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

# Opens java cli in subprocess workaround
# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess

# pyside2-uic mainwindow.ui -o UI_MainWindow.py
