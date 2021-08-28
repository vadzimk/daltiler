import json
import math
import time
from datetime import datetime

from PySide2.QtCore import Slot, QRegExp
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

        self.progressBar.setVisible(False)

        self.pushButton.setEnabled(False)
        self.pushButton_5.setVisible(False)
        self.connect_signals_and_slots()

        self.infilename = None
        self.template_filename = None
        self.infilename_n_pages = None
        self.page_start = None
        self.page_end = None
        self.output_path = None
        self.product_table_path = None
        self.coro = self.run_generator()
        self.pushButton.setText("Start")
        self.errors = []

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

    def restart(self):
        self.coro = self.run_generator()
        self.pushButton.setText("Start")

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

        self.restart()

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

    def handle_background(self, line_edit_obj, is_valid):
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
                err_msg = f"{os.path.basename(self.template_filename)}\ncontains no page range: ({self.page_start}, {self.page_end})"
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
        progress = int(math.ceil((p - self.page_start + 1) * 100 / (self.page_end - self.page_start + 1)))
        self.progressBar.setValue(min(progress, 99))
        print('progress', self.progressBar.value())

    def show_info_dialog(self, text):
        ret = QMessageBox.information(self, "Info", text, QMessageBox.StandardButton.Ok)

    def show_error_dialog(self, text):
        ret = QMessageBox.warning(self, "Error", text, QMessageBox.StandardButton.Ok)
        if ret:
            self.errors = []

    @Slot(None)
    def handle_run(self):
        ready = self.set_start_enabled() and self.check_input()
        if not ready:
            return
        try:
            next(self.coro)
        except StopIteration:
            return

    def run_generator(self):

        start_time = time.time()
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        self.pushButton_4.setEnabled(False)
        self.pushButton.setEnabled(False)
        print("progress bar is visible",self.progressBar.isVisible())
        print("progress bar value",self.progressBar.value())

        price_list = PdfDoc(
            in_file_name=self.infilename,
            template_json=self.template_filename,
            page_start=self.page_start,
            n_pages=self.page_end - self.page_start + 1
        )
        try:
            price_list.create_pages(lambda p: self.set_page_progress(p))
        except IndexError:
            err_msg = f"{self.template_filename} doesn't contain required tables"
            self.show_error_dialog(err_msg)
            self.restart()

        price_list.create_product_tables()
        price_list.construct_cumulative_dict()
        price_list.patch_cumulative_dictionary()
        timestamp = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        self.product_table_path = f'{self.output_path}/product_table.csv'
        product_table_export_success = False
        while not product_table_export_success:
            try:
                product_table_export_success = price_list.export_cumulative_dict(self.product_table_path)
                end_time = time.time()
                hours, rem = divmod(end_time - start_time, 3600)
                minutes, seconds = divmod(rem, 60)

                time_msg = f"Time elapsed: {minutes:.0f} min {seconds:.0f} sec\n"
                self.statusbar.showMessage(time_msg)

                self.show_info_dialog("Product table created!\nYou may edit it before continuing")
            except PermissionError:
                err_msg = f"{os.path.basename(self.product_table_path)}\nAccess denied. Close applications that might use it and press Continue"
                self.show_error_dialog(err_msg)
                self.pushButton.setText("Continue")
                self.pushButton.setEnabled(True)
                self.statusbar.showMessage(err_msg)
                self.pushButton_4.setEnabled(False)

                yield

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
        self.pushButton_5.clicked.connect(lambda: self.open_file(self.product_table_path))
        yield

        # continuing
        target_uom_export_success = False
        while not target_uom_export_success:
            try:
                target_uom_export_success = create_target_and_uom(
                    self.product_table_path,
                    f'{self.output_path}/target.csv',
                    f'{self.output_path}/uom.csv'
                )
                self.statusbar.clearMessage()
                self.progressBar.setValue(100)
                self.show_info_dialog("Output files created!")
            except PermissionError:
                err_msg = f"target.csv or uom.csv\nAccess denied. Close applications that might use it and press Continue"
                self.show_error_dialog(err_msg)
                self.pushButton.setText("Continue")
                self.pushButton.setEnabled(True)
                self.statusbar.showMessage(err_msg)
                self.pushButton_4.setEnabled(False)

                yield

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
        return


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
# TODO fix progress bar not showing progress
# TODO make it multithreaded
