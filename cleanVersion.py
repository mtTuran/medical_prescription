# -*- coding: utf-8 -*-

# importing necessary gui libraries
import customtkinter
from customtkinter import *
from tkinter import messagebox
from tkinter import Listbox

# importing necessary pdf writing libraries
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

import datetime  # importing datetime to write the date automatically
import csv  # importing csv module to read csv files

import win32print
# import win32api  # importing to send our pdf to printer
from subprocess import call

from PIL import Image

from PyPDF2 import PdfWriter, PdfReader
import io  # to use a pdf as a template


def align_screen(window, s_width, s_height ):
    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()
    x = (window_width/2) - (s_width/2)
    y = (window_height/2) - (s_height/2)
    window.geometry("%dx%d+%d+%d" % (s_width, s_height, x, y))


def resize_image(e):
    return


def resize_entry(e):
    return


def resize_textbox(e):
    return


# ----------------------------------------------------------------------------------------------------------------------
# initialize pdf

packet = io.BytesIO()
pdfmetrics.registerFont(TTFont('myfont', "drafts_and_prescriptions/myfont.ttf"))
addMapping('myfont', 0, 0, 'myfont')  # setting up pdf font and sheet
font_name = "myfont"
fontSize = 10

# ----------------------------------------------------------------------------------------------------------------------

root = customtkinter.CTk()
root.title("Medical Rx")

w = 1300    # 1700
h = 800     # 900
# root.wm_state('zoomed')
align_screen(root, w, h)
root.resizable(False, False)
customtkinter.set_appearance_mode('Dark')
customtkinter.set_default_color_theme('green')  # setting up the app
root.iconbitmap('photos/programIcon.ico')

today = datetime.date.today()
date = today.strftime('%d/%m/%Y')  # getting today's date


def file_exists(file_path):
    return os.path.exists(file_path)


def remove_existing_file(file_path):
    if file_exists(file_path):
        os.remove(file_path)


def openOldFiles():
    folder_path = 'Eski Reçeteler'
    try:
        os.startfile(folder_path)
    except Exception as e:
        print(f"Error opening folder: {e}")


def login():
    loginWord = '10293847'
    if password.get() == loginWord:
        loginPage.destroy()
        root.deiconify()
    else:
        messagebox.showwarning('Hatalı Şifre', 'Hatalı şifre!')


def on_closing():
    root.destroy()


def roman():
    roman_numerals = {
        1: 'I)',
        2: 'II)',
        3: 'III)',
        4: 'IV)',
        5: 'V)',
        6: 'VI)',
        7: 'VII)',
        8: 'VIII)',
        9: 'IX)',
        10: 'X)',
    }
    lines = medicines.get('1.0', 'end-1c').split('\n\n')
    n = len(lines)
    return roman_numerals[n]


def create_pdf(save_directory):
    pdf_canvas = canvas.Canvas(packet, pagesize=A5)
    pdf_canvas.setFont(font_name, fontSize)

    pdf_canvas.drawString(105, 471, patEnt.get())
    first_x = 310
    yCoor = 442
    passes = {'-', '/'}
    sickness = sicEnt.get()
    for p in sickness:
        if p in passes:
            sickness = sickness.replace(p, ',')
    sickness = sickness.split(',')
    sickness = [sick.lstrip() for sick in sickness]
    for sick in sickness:
        pdf_canvas.drawString(first_x, yCoor, sick)
        yCoor -= 12
    pdf_canvas.drawString(310, 471, datEnt.get())
    pdf_canvas.drawString(105, 441, protocolEnt.get())
    textBox = medicines.get('1.0', 'end-1c').split('\n')
    yCoor = 400
    firs_x = 30
    max_x = 360
    for t in textBox:
        def check(t_line, y_coordinat):
            while pdf_canvas.stringWidth(t_line) > max_x:
                i = len(t_line) - 1
                while pdf_canvas.stringWidth(t_line[:i]) > max_x and i > 0:
                    i -= 1
                if i == 0:
                    # Handle the case where a single word is longer than the max_x width.
                    # You may choose to truncate it or handle it differently.
                    truncated_line = t_line[:i]
                    t_line = t_line[i:]
                else:
                    # Find the last occurrence of a space to divide the line at that point.
                    while i > 0 and t_line[i] != ' ':
                        i -= 1
                    if i == 0:
                        # If no space is found, we simply cut off the word to fit within the width.
                        truncated_line = t_line[:i]
                        t_line = t_line[i:]
                    else:
                        truncated_line = t_line[:i]
                        t_line = t_line[i + 1:]  # Skip the space after the split.

                pdf_canvas.drawString(firs_x, y_coordinat, truncated_line)
                y_coordinat -= 14

            return t_line, y_coordinat

        t, yCoor = check(t, yCoor)
        pdf_canvas.drawString(firs_x, yCoor, t)
        yCoor -= 14

    pdf_canvas.save()

    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfReader(packet)
    # read your existing PDF
    existing_pdf = PdfReader(open("drafts_and_prescriptions/A5Prescription.pdf", "rb"))
    output = PdfWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # delete the pdf file with the same name to avoid further problems
    if file_exists(save_directory):
        remove_existing_file(save_directory)

    # finally, write "output" to a real file
    output_stream = open(save_directory, "wb")
    output.write(output_stream)
    output_stream.close()
    packet.seek(0)


# function to write and save our pdf
def save():
    try:
        save_directory = 'Eski Reçeteler/' + protocolEnt.get() + '-' + '.'.join(datEnt.get().split('/')) + '.pdf'
        create_pdf(save_directory)
        messagebox.showinfo('Kaydet', 'Kayıt başarılı!')
    except:
        messagebox.showinfo('Kaydet', 'Kayıt başarılı olmadı!')
    '''
    if messagebox.askyesno('Kaydet', 'PDF olarak kaydetmek istediğinize emin misiniz?'):
        directory = filedialog.asksaveasfilename(defaultextension='.pdf',
                                                 filetypes=[('PDF Files', '*.pdf')],
                                                 title='Kaydedilme dizini seçin.')
        if not directory:
            messagebox.showinfo('Kaydet', 'Kayıt iptal edildi!')
            return

        create_pdf(directory)

        messagebox.showinfo('Kaydet', 'Kayıt başarılı!')
    '''


# function to print out our pdf
def print_pdf():
    save_directory = 'Eski Reçeteler/' + protocolEnt.get() + '-' + '.'.join(datEnt.get().split('/')) + '.pdf'
    create_pdf(save_directory)
    create_pdf('print_out.pdf')
    printer_name = win32print.GetDefaultPrinter()
#    win32api.ShellExecute(0, "printto", 'print_out.pdf', '"%s' % printer_name, ".", 0)
    with open('AdobeAdress.txt', 'r', encoding='utf-8') as af:   # adobe file adress
        acrobat = af.read()
    call([acrobat, "/T", 'print_out.pdf', printer_name])


# function for updating the listbox whenever something chosen on combobox
def updateList(event):
    searchbar.delete(0, END)
    selectedD = dioClass.get()
    dioBox.delete(0, END)
    favButColor()

    with open('drafts_and_prescriptions/diogs.csv', 'r', encoding='utf-8') as uf:
        file_reader = csv.reader(uf, delimiter='|')
        for row in file_reader:
            if row[0] == selectedD:
                dioBox.insert(END, row[1])

    delPre.configure(state='disabled', fg_color='#CACFD2')  # to ensure user does not try to delete
                                                            # without choosing a prescription


# insert the chosen prescription to medicines box
def addToPre():
    if dioBox.curselection():
        blank_number = len(medicines.get('1.0', 'end-1c').split('\n\n'))
        rx = preDict[dioBox.get(ACTIVE)].split('\n')
        rx = [(' ' * (blank_number + 1)) + element for element in rx]
        rx[0] = ' ' + rx[0].lstrip()
        rx = '\n'.join(rx)
        medicines.insert(END, roman() + rx + '\n\n')
        searching = searchbar.get()
        if searching.isspace():     # if the header chosen thorugh normal means
            if dioClass.get() not in sicEnt.get():
                sicEnt.insert(END, dioClass.get() + ', ')
        else:                       # if the header is chosen thorugh searching
            with open('drafts_and_prescriptions/diogs.csv', 'r', encoding='utf-8') as dh:
                reader = csv.reader(dh, delimiter='|')
                for row in reader:
                    if row[1] == dioBox.get(ACTIVE) and row[0] not in sicEnt.get():
                        sicEnt.insert(END, row[0] + ', ')
                        return
    elif favBox.curselection():
        blank_number = len(medicines.get('1.0', 'end-1c').split('\n\n'))
        rx = preDict[favBox.get(ACTIVE)[0]].split('\n')
        rx = [(' ' * (blank_number + 1)) + element for element in rx]
        rx[0] = ' ' + rx[0].lstrip()
        rx = '\n'.join(rx)
        medicines.insert(END, roman() + rx + '\n\n')
        with open('drafts_and_prescriptions/diogs.csv', 'r', encoding='utf-8') as dh:
            reader = csv.reader(dh, delimiter='|')
            for row in reader:
                if row[1] == favBox.get(ACTIVE)[0] and row[0] not in sicEnt.get():  # probably because csv file contains
                    sicEnt.insert(END, row[0] + ', ')                 # only one column it causes logic error by sending
                    return                                            # ('item',) if not used with indexes


# opening an edit page to update an existing prescription
def openEdit():
    def saveChanges():
        try:
            with open('drafts_and_prescriptions/diogs.csv', 'r', encoding='utf-8') as nf:
                reader = csv.reader(nf, delimiter='|')
                lines = list(reader)

            newClassValue = newClass.get()
            newHeaderValue = newHeader.get()
            newPresValue = newPres.get("1.0", "end-1c")
            newPresValue = '~'.join(newPresValue.split('\n'))

            newLines = [a_line for a_line in lines if
                        a_line[0] != dioClass.get() or a_line[1] != dioBox.get(ACTIVE)]
            newLines.append([newClassValue, newHeaderValue, newPresValue])

            with open('drafts_and_prescriptions/diogs.csv', 'w', newline='', encoding='utf-8') as nf:
                writer = csv.writer(nf, delimiter='|')
                writer.writerows(newLines)

            del preDict[dioBox.get(ACTIVE)]
            preDict[newHeaderValue] = '\n'.join(newPresValue.split('~'))

            # auto refresh to add changes to gui
            if newClassValue == dioClass.get() and newHeaderValue != dioBox.get(del_item):
                dioBox.delete(del_item)
                dioBox.insert(END, newHeaderValue)

            elif newClassValue not in typeList:  # add a new type if the type name changed
                dioBox.delete(del_item)
                typeList.append(newClassValue)
                dioClass.configure(values=typeList)

            preview.configure(state='normal')
            preview.delete('0.0', 'end')
            preview.configure(state='disabled')
            messagebox.showinfo('Değişim', 'Değişim kaydedildi!')
            editWindow.destroy()

        except:
            messagebox.showinfo('Değişim', 'Değişiklik esnasında bir hata oluştu!')
            editWindow.destroy()

    del_item = dioBox.curselection()  # saving the index in case we need it. if not then next curseselection
    if del_item:  # will return empty tuple
        editWindow = CTkToplevel(root)
        align_screen(editWindow, 600, 400)
    #   editWindow.geometry("600x400")
        change = CTkButton(editWindow, text="Değişiklikleri Onayla", command=saveChanges)
        newClass = CTkEntry(editWindow, width=250, justify=CENTER, corner_radius=10)
        newHeader = CTkEntry(editWindow, width=250, justify=CENTER, corner_radius=10)
        newPres = CTkTextbox(editWindow, height=220, width=220, corner_radius=15)
        CTkLabel(editWindow, text='Sınıf:').grid(row=0, column=0, padx=30, pady=15)
        newClass.grid(row=0, column=1, padx=30, pady=15)
        CTkLabel(editWindow, text='Başlık:').grid(row=1, column=0, padx=30, pady=15)
        newHeader.grid(row=1, column=1, padx=30, pady=15)
        CTkLabel(editWindow, text='Reçete:').grid(row=2, column=0, padx=30, pady=15)
        newPres.grid(row=2, column=1, padx=30, pady=15)
        newClass.insert(0, dioClass.get())
        newHeader.insert(0, dioBox.get(del_item))
        if dioBox.get(del_item) in preDict.keys():
            newPres.insert(0.0, preDict[dioBox.get(del_item)])
            change.grid(row=2, column=2)
        editWindow.grab_set()  # keep the focus on top window


# opening an edit page to add a new prescription
def openAdd():
    def addElement():
        try:
            addClassValue = addClass.get()
            addHeaderValue = addHeader.get()
            addPresValue = addPres.get("1.0", "end-1c")
            addPresValue = '~'.join(addPresValue.split('\n'))
            appendData = [addClassValue, addHeaderValue, addPresValue]
            with open('drafts_and_prescriptions/diogs.csv', 'a', newline='', encoding='utf-8') as af:  # append file
                appender = csv.writer(af, delimiter='|')
                appender.writerow(appendData)
            messagebox.showinfo('Ekleme', 'Ekleme Başarılı!')
            preDict[addHeaderValue] = '\n'.join(addPresValue.split('~'))
            if addClassValue not in typeList:  # add the new class to gui
                typeList.append(addClassValue)
                dioClass.configure(values=typeList)
                classes.insert(END, addClassValue)
            elif addClassValue == dioClass.get():  # auto refresh to add new prescription to gui
                dioBox.insert(END, addHeaderValue)

        except:
            messagebox.showinfo('Ekleme', 'Ekleme Başarısız!')

    def insertToClass(ee):
        if classes.curselection():
            addClass.delete(0, END)
            addClass.insert(0, classes.get(classes.curselection()))

    addWindow = CTkToplevel(root)
    align_screen(addWindow, 600, 400)
#   addWindow.geometry("600x400")
    addWindow.resizable(False, False)
    classes = Listbox(addWindow, bg='#263238', fg='white', font=15, borderwidth=0, highlightthickness=0)
    for i in typeList:
        classes.insert(END, i)
    classes.bind('<<ListboxSelect>>', insertToClass)  # chosen class will be inserted automatically
    addButton = CTkButton(addWindow, text="Eklemeyi Onayla", command=addElement)
    addClass = CTkEntry(addWindow, width=250, justify=CENTER, corner_radius=10)
    addHeader = CTkEntry(addWindow, width=250, justify=CENTER, corner_radius=10)
    addPres = CTkTextbox(addWindow, height=220, width=220, corner_radius=15)
    CTkLabel(addWindow, text='Sınıf:').grid(row=0, column=0, padx=30, pady=15)
    addClass.grid(row=0, column=1, padx=30, pady=15)
    CTkLabel(addWindow, text='Başlık:').grid(row=1, column=0, padx=30, pady=15)
    addHeader.grid(row=1, column=1, padx=30, pady=15)
    CTkLabel(addWindow, text='Rx:').grid(row=2, column=0, padx=30, pady=15)
    addPres.grid(row=2, column=1, padx=30, pady=15)
    addButton.grid(row=2, column=2)
    classes.grid(row=1, column=2)

    addWindow.grab_set()  # keep the focus on top window


# function to delete an existing prescription
def deletePres():
    if messagebox.askyesno('Element Silme', 'Bu reçeteyi silmek istediğinize emin misiniz?'):
        item = dioBox.get(ACTIVE)
        try:
            with open('drafts_and_prescriptions/diogs.csv', 'r', encoding='utf-8') as dh:  # delete header
                holder = csv.reader(dh, delimiter='|')
                oldLines = list(holder)
            newLines = [oldLine for oldLine in oldLines if oldLine[1] != item]
            with open('drafts_and_prescriptions/diogs.csv', 'w', newline='', encoding='utf-8') as wh:  # write header
                writer = csv.writer(wh, delimiter='|')
                writer.writerows(newLines)
            del preDict[item]
            messagebox.showinfo('Element Silme', 'Silme Başarılı!')

        except:
            messagebox.showinfo('Element Silme', 'Silme Başarısız!')

        if item in favBox.get(0, 'end'):
            try:
                with open('drafts_and_prescriptions/favs.csv', 'r', encoding='utf-8') as ff:  # delete from favs csv
                    ex_favs = csv.reader(ff, delimiter='|')
                    oldFavs = list(ex_favs)
                newFavs = [oldFav for oldFav in oldFavs if oldFav[0] != item]
                with open('drafts_and_prescriptions/favs.csv', 'w', newline='', encoding='utf-8') as wf:  # write fav
                    writer = csv.writer(wf, delimiter='|')
                    writer.writerows(newFavs)

                items = favBox.get(0, END)
                for index, a_item in enumerate(items):
                    if a_item == item:
                        favBox.delete(index)
                        break

            except:
                messagebox.showwarning('Fav Çıkarma', 'Silinen öğeyi favorilerden çıkarırken bir hata oluştu!')

        # auto refresh to remove prescription from gui
        del_index = dioBox.curselection()
        dioBox.delete(del_index)
        preview.configure(state='normal')
        preview.delete('0.0', 'end')
        preview.configure(state='disabled')


# function to delete all prescriptions under a certain type
def deleteClass():
    def remove_items_from_listbox(listbox, items_to_remove):    # function to delete all favs under a certain type
        listbox_items = listbox.get(0, END)
        removed_listbox_items = []
        for item in listbox_items:  # save the removed item names to delete them from the favs.csv later
            if item in items_to_remove:
                removed_listbox_items.append(item)

        listbox_items = sorted([fav for fav in listbox_items if fav not in items_to_remove])  # remove the deleted items
        listbox.delete(0, END)  # clear the favBox
        for new in listbox_items:      # refill the favBox
            listbox.insert(END, new)

        with open('drafts_and_prescriptions/favs.csv', 'r', encoding='utf-8') as ff:  # delete from favs csv
            ex_favs = csv.reader(ff, delimiter='|')
            oldFavs = list(ex_favs)
        newFavs = [oldFav for oldFav in oldFavs if oldFav[0] not in removed_listbox_items]

        with open('drafts_and_prescriptions/favs.csv', 'w', newline='', encoding='utf-8') as wf:  # write fav
            writer = csv.writer(wf, delimiter='|')
            writer.writerows(newFavs)

    if messagebox.askyesno('Sekme Silme', 'Bu sekmeyi silmek istediğinize emin misiniz? Bu sekme altındaki tüm'
                                        'reçeteler kaybolacaktır!'):
        preType = dioClass.get()
        try:
            with open('drafts_and_prescriptions/diogs.csv', 'r', encoding='utf-8') as dc:  # delete class
                cReader = csv.reader(dc, delimiter='|')
                cLines = list(cReader)
            deletedHeaders = []  # deleted header names
            uLines = []  # updated lines
            for cLine in cLines:
                if cLine[0] != preType:
                    uLines.append(cLine)
                else:
                    deletedHeaders.append(cLine[1])
            with open('drafts_and_prescriptions/diogs.csv', 'w', newline='', encoding='utf-8') as wc:  # write class
                cWriter = csv.writer(wc, delimiter='|')
                cWriter.writerows(uLines)
            for header in deletedHeaders:
                del preDict[header]

            remove_items_from_listbox(favBox, deletedHeaders)

            # auto refresh
            typeList.remove(preType)
            dioClass.set('İlaç Tipi Seç...')
            dioClass.configure(values=typeList)
            dioBox.delete(0, END)
            preview.configure(state='normal')
            preview.delete('0.0', 'end')
            preview.configure(state='disabled')

            messagebox.showinfo('Tip Silme', 'Bu tip ve altındaki tüm reçeteler silinmiştir!')

        except Exception as e:
            print(e)
            messagebox.showinfo('Tip Silme', 'Tip silme başarısız!')


def favButColor():
    if dioBox.curselection():
        addFavBut.configure(state='normal')
        addFavBut.configure(fg_color='#2FA572', hover_color='#106A43')
    elif favBox.curselection():
        addFavBut.configure(state='normal')
        addFavBut.configure(fg_color='#CC0000', hover_color='#7B241C')
    else:
        addFavBut.configure(fg_color='#CACFD2', state='disabled')
        preview.configure(state='normal')
        preview.delete('0.0', 'end')
        preview.configure(state='disabled')


# function to preview the selected prescription
def preView(e):
    favButColor()
    if dioBox.curselection():  # we add this line because when we deselect something from the listbox it still
        if dioBox.get(dioBox.curselection()) in preDict.keys():  # tries to send an empty index ''
            preview.configure(state='normal')
            preview.delete('0.0', 'end')
            preview.insert('0.0', preDict[dioBox.get(dioBox.curselection())])  # use curse selection instead of active
            preview.configure(state='disabled')  # since active'll use the previous selection
        delPre.configure(state='normal', fg_color='#CC0000', hover_color='#7B241C')

    else:
        delPre.configure(state='disabled', fg_color='#CACFD2')  # to ensure user does not try to
                                                                # delete without choosing a prescription


# function to clean entries
def clean():
    patEnt.delete(0, END)
    protocolEnt.delete(0, END)
    sicEnt.delete(0, END)
    medicines.delete('0.0', 'end')
    preview.configure(state='normal')
    preview.delete('0.0', 'end')
    preview.configure(state='disabled')


def search(d):
    searching = searchbar.get().lower()
    if searching == '':
        dioClass.set('İlaç Tipi Seç...')
        dioBox.delete(0, END)
        return
    elif searching != '':
        dioClass.set('Aranıyor...')
        searchList = []
        with open('drafts_and_prescriptions/diogs.csv', 'r', encoding='utf-8') as sf:   # search file
            fileR = csv.reader(sf, delimiter='|')
            for ar in fileR:    # a row
                if searching in ar[0].lower() or searching in ar[1].lower() or searching in ar[2].lower():
                    searchList.append(ar[1])
        dioBox.delete(0, END)
        for result in searchList:
            dioBox.insert(END, result)


def preViewFav(f):
    favButColor()
    selected_fav_index = favBox.curselection()
    if selected_fav_index:  # we add this line because when we deselect something from the listbox it still
        selected_fav_item = favBox.get(selected_fav_index)
        if selected_fav_item[0] in preDict.keys():  # tries to send an empty index ''
            preview.configure(state='normal')
            preview.delete('0.0', 'end')
            preview.insert('0.0', preDict[selected_fav_item[0]])  # not giving an index results with key error
            preview.configure(state='disabled')                   # ('selected_item',)


def remove_fav():
    oldFavIndex = favBox.curselection()
    if oldFavIndex:
        try:
            removing = favBox.get(oldFavIndex)[0]

            with open('drafts_and_prescriptions/favs.csv', 'r', encoding='utf-8') as ff:  # delete from favs csv
                ex_favs = csv.reader(ff, delimiter='|')
                oldFavs = list(ex_favs)
            newFavs = [oldFav for oldFav in oldFavs if oldFav[0] != removing]

            with open('drafts_and_prescriptions/favs.csv', 'w', newline='', encoding='utf-8') as wf:  # write fav
                writer = csv.writer(wf, delimiter='|')
                writer.writerows(newFavs)

            favBox.delete(oldFavIndex)

            preview.configure(state='normal')
            preview.delete('0.0', 'end')
            preview.configure(state='disabled')

        except:
            messagebox.showwarning('Fav Çıkarma', 'Favorilerden çıkarma yaparken bir hata oluştu!')


def addToFav():
    selected_index = dioBox.curselection()
    if selected_index:
        selected_item = dioBox.get(selected_index)
        if selected_item not in favBox.get(0, 'end'):
            try:
                new_fav = [selected_item]
                with open('drafts_and_prescriptions/favs.csv', 'a', newline='', encoding='utf-8') as ff:
                    fav_writer = csv.writer(ff, delimiter='|')
                    fav_writer.writerow(new_fav)
                favBox.insert(END, new_fav[0])
            except:
                messagebox.showwarning('Fav Ekleme', 'Favorilere ekleme yaparken bir hata oluştu!')

    elif favBox.curselection():
        remove_fav()


# downloading the existing prescriptions to program
with open('drafts_and_prescriptions/diogs.csv', 'r', encoding='utf-8') as rf:
    csv_reader = csv.reader(rf, delimiter='|')
    typeList = []
    preDict = dict()
    for line in csv_reader:
        if line and len(line) >= 2:
            if line[0] not in typeList:
                typeList.append(line[0])

            preDict[line[1]] = '\n'.join(line[2].split('~'))

favFrame = CTkFrame(root, corner_radius=10)  # creating a frame for favorites
bind = CTkFrame(root, corner_radius=10)  # creating a frame for dropdown menu and listbox
dioClass = CTkComboBox(bind, values=typeList, command=updateList,
                       corner_radius=15)  # combobox to choose a medicine type
# Listbox to show and choose prescriptions under a medicine type
dioBox = Listbox(bind, bg='#263238', fg='white', borderwidth=0, highlightthickness=0)
dioBox.config(width=35, height=20, font=15)         # w15, h20
dioBox.bind('<<ListboxSelect>>', preView)  # bind our prescription box to preview

# Listbox to list favorites
favBox = Listbox(bind, bg='#263238', fg='white', borderwidth=0, highlightthickness=0)
favBox.config(width=35, height=20, font=15)         # w35 h20
favBox.bind('<<ListboxSelect>>', preViewFav)  # bind our fav prescription box to preview
# !!! this listbox source is a csv file, but it only contains one column, for that reason I think it gives error !!!
#     when .get(.curselection) is not used with an index

# downloading existing favs
with open('drafts_and_prescriptions/favs.csv', 'r', encoding='utf-8') as rfav:
    inserter = csv.reader(rfav, delimiter='|')
    for fav in inserter:
        if fav and len(fav) >= 1:
            favBox.insert(END, fav)


# creating images to use in buttons
cleanImage = CTkImage(Image.open('photos/resetBut.png'), size=(20, 20))
addImage = CTkImage(Image.open('photos/addBut.png'), size=(20, 20))
editImage = CTkImage(Image.open('photos/editBut.png'), size=(20, 20))
delPreImage = CTkImage(Image.open('photos/delPreBut.png'), size=(20, 20))
delClaImage = CTkImage(Image.open('photos/delClaBut.png'), size=(20, 20))
saveImage = CTkImage(Image.open('photos/saveBut.png'), size=(20, 20))
printImage = CTkImage(Image.open('photos/printBut.png'), size=(20, 20))
addToPreImage = CTkImage(Image.open('photos/addToPreBut.png'), size=(20, 20))
oldFilesImage = CTkImage(Image.open('photos/lib.png'), size=(20, 20))
favImage = CTkImage(Image.open('photos/heart.png'), size=(20, 20))
hosImage = CTkImage(Image.open('photos/g.png'), size=(73, 108))    # 147, 216

# creating entries
patEnt = CTkEntry(root, width=200, justify=LEFT, corner_radius=10)          # width 250
protocolEnt = CTkEntry(root, width=200, justify=LEFT, corner_radius=10)
sicEnt = CTkEntry(root, width=200, justify=LEFT, corner_radius=10)
datEnt = CTkEntry(root, width=150, justify=CENTER, corner_radius=10)        # width 150
medicines = CTkTextbox(root, height=500, width=450, corner_radius=15)       # h500 w550
preview = CTkTextbox(bind, height=220, width=220, corner_radius=15)         # 220 220
searchbar = CTkEntry(root, width=175, justify=LEFT, corner_radius=20)       # w250

# creating buttons
insertBut = CTkButton(bind, text="Reçetele", command=addToPre, corner_radius=10, image=addToPreImage, compound='left')
edit = CTkButton(bind, text='Edit', command=openEdit, image=editImage, compound='left', corner_radius=10)
add = CTkButton(bind, text='Ekle', command=openAdd, corner_radius=10, image=addImage, compound='left')
delPre = CTkButton(bind, text='Reçeteyi Sil', command=deletePres, corner_radius=10, image=delPreImage, compound='left')
delCla = CTkButton(bind, text='Sekmeyi Sil', command=deleteClass, corner_radius=10, image=delClaImage, compound='left')
saveButton = CTkButton(root, text="Kaydet", command=save, corner_radius=10, image=saveImage, compound='left')
printButton = CTkButton(root, text="Yazdır", command=print_pdf, corner_radius=10, image=printImage, compound='left')
reset = CTkButton(root, text='Temizle', image=cleanImage, command=clean, corner_radius=10, compound='left')
oldFilesButton = CTkButton(root, image=oldFilesImage, corner_radius=10, text='Eski Reçeteler', command=openOldFiles)
addFavBut = CTkButton(bind, corner_radius=10, text='', width=25, image=favImage, command=addToFav, state='disabled',
                      fg_color='#CACFD2')
# remFavBut = CTkButton(bind, corner_radius=10, text='Favorilerden Çıkar', command=remove_fav)

oldFilesButton.configure(fg_color='#FBC02D', hover_color='#9A7D0A', text_color='black')
delPre.configure(fg_color='#CACFD2', text_color='black', state='disabled', text_color_disabled='#757575')  # can't click
delCla.configure(fg_color='#CC0000', hover_color='#7B241C', text_color='black')                  # until a pres selected
edit.configure(fg_color='#FBC02D', hover_color='#9A7D0A', text_color='black')
add.configure(fg_color='#FBC02D', hover_color='#9A7D0A', text_color='black')
insertBut.configure(text_color='black')
saveButton.configure(fg_color='#0033FF', hover_color='#3333CC', text_color='black')
printButton.configure(fg_color='#0033FF', hover_color='#3333CC', text_color='black')
reset.configure(text_color='black')
# addFavBut.configure(fg_color='#FBC02D', hover_color='#9A7D0A', text_color='black')
# remFavBut.configure(fg_color='#CC0000', hover_color='#7B241C', text_color='black')

# Layout
CTkLabel(root, text='Hastanın Tam Adı:').grid(row=0, column=0, padx=15, pady=15)
patEnt.grid(row=0, column=1, padx=30, pady=15)
CTkLabel(root, text='Protokol No:').grid(row=1, column=0, padx=15, pady=15, sticky='n')
protocolEnt.grid(row=1, column=1, padx=30, pady=15, sticky='n')
CTkLabel(root, text='Hastalığın Tanısı:').grid(row=2, column=0, padx=15, pady=15, sticky='n')
sicEnt.grid(row=2, column=1, padx=30, pady=15, sticky='n')
CTkLabel(root, text='Tarih:').grid(row=0, column=3, padx=15, pady=15)
datEnt.grid(row=0, column=4, padx=30, pady=15)
CTkLabel(root, text='Reçete:').grid(row=3, column=0, padx=15, pady=15, sticky='n')
medicines.grid(row=4, column=0, columnspan=3, padx=30, pady=15, sticky='n')
saveButton.grid(row=1, column=4, pady=15, sticky='n')
printButton.grid(row=1, column=7, pady=15, sticky='n')
reset.grid(row=0, column=7)
oldFilesButton.grid(row=0, column=5)

bind.grid(row=2, rowspan=5, column=4, columnspan=4, sticky='we')

dioClass.grid(row=0, column=0, columnspan=4, padx=15, pady=15)
delCla.grid(row=0, column=3, padx=15, pady=15)
dioBox.grid(row=1, column=0, rowspan=3, columnspan=2, padx=15, pady=15, sticky='w')
insertBut.grid(row=4, column=0, padx=15, pady=15)
add.grid(row=4, column=1, padx=15, pady=15)
edit.grid(row=4, column=2, padx=15, pady=15)
delPre.grid(row=4, column=3, padx=15, pady=15)
preview.grid(row=5, column=1, sticky='we', columnspan=2)
searchbar.grid(row=1, column=5, pady=15, sticky='n')

# favFrame.grid(row=2, rowspan=5, column=8, columnspan=4, sticky='we')    # rs5, cs8
favBox.grid(row=1, column=2, rowspan=3, columnspan=2, padx=15, pady=15, sticky='e')
addFavBut.grid(row=2, column=0, columnspan=4, padx=15, pady=15, sticky='s')
# remFavBut.grid(row=3, column=0, columnspan=4, padx=15, pady=15, sticky='n')

searchbar.bind('<KeyRelease>', search)

logoImage = CTkLabel(bind, image=hosImage, text='')
logoImage.grid(row=3, column=0, columnspan=4)

# initial values
datEnt.insert(0, date)  # set the date automatically
dioClass.set('İlaç Tipi Seç...')  # set a starting string value for combobox

# create the login page and hide the root page
loginPage = CTkToplevel(root)
align_screen(loginPage, 460, 280)
# loginPage.geometry('460x280')
loginPage.resizable(False, False)
loginPage.title('Giriş Yap')
loginPage.protocol("WM_DELETE_WINDOW", on_closing)
CTkLabel(loginPage, text='Lütfen Şifrenizi Giriniz...').grid(row=0, column=2, columnspan=3, sticky='ns',
                                                             padx=100, pady=30)
password = CTkEntry(loginPage, show='*', width=250, corner_radius=10, justify='center')
password.grid(row=1, column=2, columnspan=3, sticky='ns', padx=100, pady=30)
loginButton = CTkButton(loginPage, text='Giriş Yap', command=login)
loginButton.grid(row=2, column=2, sticky='ns', columnspan=3, padx=100, pady=30)

root.withdraw()  # hide the root window until the password entered

root.mainloop()
