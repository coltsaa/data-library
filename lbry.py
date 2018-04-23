# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @author:'ryo'
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox as mBox
from datetime import datetime, timedelta
import pymssql


class MSSQL:
    """
    对pymssql的简单封装

    """

    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):
        """
        得到连接信息
        返回: conn.cursor()
        """
        if not self.db:
            raise NameError
        self.conn = pymssql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            database=self.db,
            charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise NameError
        else:
            return cur

    def ExecQuery(self, sql):
        """
        执行查询语句
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段
        """
        try:
            cur = self.__GetConnect()
            cur.execute(sql)
            resList = cur.fetchall()
            self.conn.close()
            return resList
        except Exception as err:
            mBox.showerror('error','System crashed...Please retry\nReason:\n{}'.format(err))

    def ExecNonQuery(self, sql):
        """
        执行非查询语句

        """
        try:
            cur = self.__GetConnect()
            cur.execute(sql)
            cur.close()
            self.conn.commit()
            self.conn.close()
        except Exception as err:
            mBox.showerror('error', 'System crashed...Please retry\nReason:\n{}'.format(err))
            self.conn.rollback()
            self.conn.close()


class ToolTip(object):
    def __init__(self, widget):

        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    # ===========================================================


if __name__ == '__main__':
    def main():
        # 数据库链接
        ms = MSSQL(host="localhost", user="ryo", pwd="666666", db="LibraryX")
        # 共用部分
        before = ('书号:', '书名:', '作者:', '价格:', '出版社:', '简介:', '分类:')
        front = ('编号:', '人名:', '余额:', '公司:', '职位:')
        beforeLend = ('书号:', '书名:', '编号:', '人名:', '借书日期:', '应还日期:')
        beforeReturn = ('书号:', '书名:', '编号:', '人名:', '还书日期:')
        category = ('外国文学', '中国文学', '日本文学', '古典文学', '推理小说', '魔幻小说', '科幻小说')

        # 创建tip
        def createToolTip(widget, text):
            toolTip = ToolTip(widget)

            def enter(event):
                toolTip.showtip(text)

            def leave(event):
                toolTip.hidetip()

            widget.bind('<Enter>', enter)
            widget.bind('<Leave>', leave)

        # 提示信息
        def msgBoxInfoAbout():
            mBox.showinfo('Info', 'Call me\nif u r in trouble')

        # 回馈信息
        def msgBoxFeedback():
            result = mBox.askyesno('Feedback', 'Do u like my design?')
            if result:
                mBox.showinfo('Bingo', 'How SMART u r!')
            else:
                mBox.showinfo('Emm...', 'u must click the wrong one')

        # 按书号查询
        def getBookByBno():
            try:
                num = bookNumChosen.get()
                bnoList = []
                resListBno = ms.ExecQuery("SELECT Bno FROM Books")
                for infoBno in resListBno:
                    bnoList.append(infoBno[0])
                if num:
                    if num in bnoList:
                        resList = ms.ExecQuery(
                            "SELECT * FROM Books WHERE Bno = '{}'".format(num))
                        infoList = resList[0]
                        text.delete(1.0, END)
                        for item in range(6):
                            text.insert(INSERT, before[item])
                            text.insert(INSERT, infoList[item])
                            text.insert(INSERT, '\n')
                        resList_extra = ms.ExecQuery(
                            u"SELECT * FROM Category WHERE Bno = '{}'".format(num))[0]
                        text.insert(INSERT, before[6])
                        text.insert(INSERT, resList_extra[1])
                    else:
                        mBox.showerror('Error', 'the book is not existed!')
                else:
                    mBox.showwarning('Warning', 'did not input any book!')
            except BaseException:
                text.delete(1.0, END)
                text.insert(INSERT, 'System crashed...Please retry')
            return

        # 按书名查询
        def getBookByBname():
            try:
                name = bookNameChosen.get()
                bnameList = []
                resListBname = ms.ExecQuery("SELECT Bname FROM Books")
                for infoBname in resListBname:
                    bnameList.append(infoBname[0])
                if name:
                    if name in bnameList:
                        resList = ms.ExecQuery(
                            u"SELECT * FROM BookInfo WHERE Bname = '{}'".format(name))[0]
                        text.delete(1.0, END)
                        for item in range(7):
                            text.insert(INSERT, before[item])
                            text.insert(INSERT, resList[item])
                            text.insert(INSERT, '\n')
                    else:
                        mBox.showerror('Error', 'the book is not existed!')
                else:
                    mBox.showwarning('Warning', 'did not input any book!')
            except BaseException:
                text.delete(1.0, END)
                text.insert(INSERT, 'System crashed...Please retry')
            return

        # 添加书籍
        def addBooks():
            num = ent1.get()
            name = ent2.get()
            author = ent3.get()
            price = ent4.get()
            publish = ent5.get()
            summary = ent6.get()
            type_ = typeChosen.get()
            bnoList = []
            resListBno = ms.ExecQuery("SELECT Bno FROM Books")
            for infoBno in resListBno:
                bnoList.append(infoBno[0])
            if num and name and author and price and publish and summary and type_:
                if num not in bnoList:
                    # sql = u"INSERT INTO Books VALUES('{}','{}','{}',{},'{}','{}')".format(
                    #     num, name, author, price, publish, summary)
                    # ms.ExecNonQuery(sql)
                    # sql1 = u"INSERT INTO Category VALUES('{}','{}')".format(
                    #     num, type_)
                    # ms.ExecNonQuery(sql1)
                    sql2 = u"EXEC books_insert '{}','{}','{}',{},'{}','{}','{}'".format(num, name, author, price, publish, summary, type_)
                    ms.ExecNonQuery(sql2)
                    ent1.delete(0, END)
                    ent2.delete(0, END)
                    ent3.delete(0, END)
                    ent4.delete(0, END)
                    ent5.delete(0, END)
                    ent6.delete(0, END)
                    typeChosen.current()
                    mBox.showinfo(
                        'Succeed', 'Completed!\n')
                else:
                    mBox.showerror('Error', 'The book is existed!')
            else:
                mBox.showwarning('Warning', 'Elements are not completed!')
            return

        # 确认删除书籍信息
        def checkBooks():
            name = checkBookNameChosen.get()
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            if name:
                if name in bnameList:
                    resList = ms.ExecQuery(
                        u"SELECT * FROM Books WHERE Bname = '{}'".format(name))
                    infoList = resList[0]
                    text1.delete(1.0, END)
                    for item in range(6):
                        text1.insert(INSERT, before[item])
                        text1.insert(INSERT, infoList[item])
                        text1.insert(INSERT, '\n')
                else:
                    mBox.showerror('Error', 'The book is not existed!')
            else:
                mBox.showwarning('Warning', 'Why don\'t u choose one?')
            return

        # 删除书籍前先触发判断再操作
        def deleteBooks():
            if not checkBookNameChosen.get():
                mBox.showwarning('Warning', 'Why don\'t u choose one?')
            else:
                answer = mBox.askyesno('WARNING', 'Are u SURE to DELETE')
                if answer:
                    deleteBook = checkBookNameChosen.get()
                    bnameList = []
                    resListBname = ms.ExecQuery("SELECT Bname FROM Books")
                    for infoBname in resListBname:
                        bnameList.append(infoBname[0])
                    if deleteBook in bnameList:
                        sql = u"DELETE FROM Books WHERE Bname = '{}'".format(
                            deleteBook)
                        sql1 = u"DELETE FROM Category WHERE Bno = (SELECT Bno FROM Books WHERE Bname ='{}')".format(
                            deleteBook)
                        sql2 = u"DELETE FROM Depot WHERE Bno = (SELECT Bno FROM Books WHERE Bname = '{}')".format(
                            deleteBook)
                        sql3 = u"DELETE FROM BookLend WHERE Bno = (SELECT Bno FROM Books WHERE Bname = '{}')".format(
                            deleteBook)
                        sql4 = u"DELETE FROM BookReturn WHERE Bno = (SELECT Bno FROM Books WHERE Bname = '{}')".format(
                            deleteBook)
                        ms.ExecNonQuery(sql4)
                        ms.ExecNonQuery(sql3)
                        ms.ExecNonQuery(sql2)
                        ms.ExecNonQuery(sql1)
                        ms.ExecNonQuery(sql)
                        checkBookNameChosen.current()
                        text1.delete(1.0, END)
                        mBox.showinfo(
                            'Succeed', 'Completed!\n')
                    else:
                        mBox.showerror('Error', 'The book is not existed!')
                else:
                    return

        # 修改书籍 根据选定项和提供数据修改
        def updateBooks():
            varBTable = chVar_B.get()
            varPTable = chVar_P.get()
            varBCol = radVar_B.get() + 1
            varPCol = radVar_P.get() + 1
            bookName = bookNameChosen2.get()
            peopleName = peopleNameChosen.get()
            updateData = ent7.get()
            bCol = [
                'Bno',
                'Bname',
                'Bauthor',
                'Bprice',
                'Bpublish',
                'Bsummary',
            ]
            pCol = [
                'Pno',
                'Pname',
                'Pmoney',
                'Punit',
                'Pjob']
            if varBTable == 1 and varPTable == 0:
                if bookName:
                    if varBCol and varBCol != 100 and varBCol != 4:
                        if updateData:
                            sql = u"UPDATE Books SET {}='{}' WHERE Bname='{}'".format(
                                bCol[varBCol - 1], updateData, bookName)
                            ms.ExecNonQuery(sql)
                            mBox.showinfo(
                                'Succeed', 'Completed!\n')
                        else:
                            mBox.showwarning(
                                'Warning', 'did not input any data!')
                    elif varBCol == 4:
                        if updateData:
                            sql = u"UPDATE Books SET {}={} WHERE Bname='{}'".format(
                                bCol[varBCol - 1], updateData, bookName)
                            ms.ExecNonQuery(sql)
                            mBox.showinfo(
                                'Succeed', 'Completed!\n')
                        else:
                            mBox.showwarning(
                                'Warning', 'did not input any data!')
                    else:
                        mBox.showwarning(
                            'Warning', 'did not select any column!')
                else:
                    mBox.showwarning('Warning', 'did not select any book!')
            elif varBTable == 0 and varPTable == 1:
                if peopleName:
                    if varPCol and varPCol != 100 and varPCol != 3:
                        if updateData:
                            sql = u"UPDATE People SET {}='{}' WHERE Pname='{}'".format(
                                pCol[varPCol - 1], updateData, peopleName)
                            ms.ExecNonQuery(sql)
                            mBox.showinfo(
                                'Succeed', 'Completed!\n')
                        else:
                            mBox.showwarning(
                                'Warning', 'did not input any data!')
                    elif varPCol == 3:
                        if updateData:
                            sql = u"UPDATE People SET {}={} WHERE Pname='{}'".format(
                                pCol[varPCol - 1], updateData, peopleName)
                            ms.ExecNonQuery(sql)
                            mBox.showinfo(
                                'Succeed', 'Completed!\n')
                        else:
                            mBox.showwarning(
                                'Warning', 'did not input any data!')
                    else:
                        mBox.showwarning(
                            'Warning', 'did not select any column!')
                else:
                    mBox.showwarning('Warning', 'did not select any people!')
            else:
                mBox.showwarning('Warning', 'did not select any table!')

        # 添加用户
        def addPeople():
            num = ent9.get()
            name = ent10.get()
            money = ent11.get()
            unit = ent12.get()
            job = ent13.get()
            pnoList = []
            resListPno = ms.ExecQuery("SELECT Pno FROM People")
            for infoBno in resListPno:
                pnoList.append(infoBno[0])
            if num and name and money and unit and job:
                if num not in pnoList:
                    sql = u"INSERT INTO People VALUES('{}','{}',{},'{}','{}')".format(
                        num, name, money, unit, job)
                    ms.ExecNonQuery(sql)
                    ent9.delete(0, END)
                    ent10.delete(0, END)
                    ent11.delete(0, END)
                    ent12.delete(0, END)
                    ent13.delete(0, END)
                    mBox.showinfo(
                        'Succeed', 'Completed!\n')
                else:
                    mBox.showerror('Error', 'The book is existed!')
            else:
                mBox.showwarning('Warning', 'Elements are not completed!')
            return

        # 查询用户
        def checkPeople():
            name = peopleNameChosen2.get()
            pnameList = []
            resListPname = ms.ExecQuery("SELECT Pname FROM People")
            for infoPname in resListPname:
                pnameList.append(infoPname[0])
            if name:
                if name in pnameList:
                    resList = ms.ExecQuery(
                        u"SELECT * FROM People WHERE Pname = '{}'".format(name))
                    infoList = resList[0]
                    text3.delete(1.0, END)
                    for item in range(5):
                        text3.insert(INSERT, front[item])
                        text3.insert(INSERT, infoList[item])
                        text3.insert(INSERT, '\n')
                else:
                    mBox.showerror('Error', 'The people is not existed!')
            else:
                mBox.showwarning('Warning', 'Why don\'t u choose one?')
            return

        # 删除用户
        def deletePeople():
            if not peopleNameChosen2.get():
                mBox.showwarning('Warning', 'Why don\'t u choose one?')
            else:
                answer = mBox.askyesno('WARNING', 'Are u SURE to DELETE?')
                if answer:
                    deletePeople = peopleNameChosen2.get()
                    pnameList = []
                    resListPname = ms.ExecQuery("SELECT Pname FROM People")
                    for infoPname in resListPname:
                        pnameList.append(infoPname[0])
                    if deletePeople in pnameList:
                        sql = u"DELETE FROM People WHERE Pname = '{}'".format(
                            deletePeople)
                        sql1 = u"DELETE FROM BookLend WHERE Pname = '{}'".format(
                            deletePeople)
                        sql2 = u"DELETE FROM BookReturn WHERE Pname = '{}'".format(
                            deletePeople)
                        ms.ExecNonQuery(sql2)
                        ms.ExecNonQuery(sql1)
                        ms.ExecNonQuery(sql)
                        peopleNameChosen2.current()
                        text3.delete(1.0, END)
                        mBox.showinfo(
                            'Succeed', 'Completed!\n')
                    else:
                        mBox.showerror('Error', 'The people is not existed!')
                else:
                    return

        #借书
        def lendBooks():
            bName = bookNameChosen4.get()
            pName = peopleNameChosen3.get()
            year = int(spin1.get())
            month = int(spin2.get())
            day = int(spin3.get())
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            pnameList = []
            resListPname = ms.ExecQuery("SELECT Pname FROM People")
            for infoPname in resListPname:
                pnameList.append(infoPname[0])
            resListBP = ms.ExecQuery("SELECT Bno,Pno FROM BookLend")
            if bName and pName:
                if bName in bnameList:
                    if pName in pnameList:
                        bNo = ms.ExecQuery(u"SELECT Bno FROM Books WHERE Bname='{}'".format(bName))[0]
                        pNo = ms.ExecQuery(u"SELECT Pno FROM People WHERE Pname='{}'".format(pName))[0]
                        if (bNo[0],pNo[0]) not in resListBP:
                            dateText = '{}/{}/{}'.format(year, month, day)
                            remain = ms.ExecQuery(u"SELECT Bremain FROM Depot WHERE Bno='{}'".format(bNo[0]))[0]
                            sql = u"INSERT INTO BookLend VALUES ('{}','{}','{}',0)".format(pNo[0], bNo[0], dateText)
                            sql1 = u"UPDATE Depot SET Bremain = ({}-1) WHERE Bno in (SELECT Bno FROM Books WHERE Bname='{}')".format(remain[0],bName)
                            ms.ExecNonQuery(sql)
                            ms.ExecNonQuery(sql1)
                            mBox.showinfo('Succeed', 'Completed!\n')
                        else:
                            mBox.showerror('Error','existed record!')
                    else:
                        mBox.showerror('Error','the people is not existed!')
                else:
                    mBox.showerror('Error','the book is not existed!')
            else:
                mBox.showwarning('Warning','both options should be selected!')

        #查询借书记录
        def checkLendRecord():
            bName = bookNameChosen4.get()
            pName = peopleNameChosen3.get()
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            pnameList = []
            resListPname = ms.ExecQuery("SELECT Pname FROM People")
            for infoPname in resListPname:
                pnameList.append(infoPname[0])
            resListBP = ms.ExecQuery("SELECT Bno,Pno FROM BookLend")
            if bName and pName:
                if bName in bnameList:
                    if pName in pnameList:
                        bNo = ms.ExecQuery(u"SELECT Bno FROM Books WHERE Bname='{}'".format(bName))[0]
                        pNo = ms.ExecQuery(u"SELECT Pno FROM People WHERE Pname='{}'".format(pName))[0]
                        if (bNo[0], pNo[0]) in resListBP:
                            sql = u"SELECT * FROM LendInfo WHERE Bno='{}' AND Pno='{}'".format(bNo[0],pNo[0])
                            res = ms.ExecQuery(sql)[0]
                            text4.delete(1.0, END)
                            text4.insert(INSERT, '\n')
                            for item in range(5):
                                text4.insert(INSERT, beforeLend[item])
                                text4.insert(INSERT, res[item])
                                text4.insert(INSERT, '\n')
                            dateText = res[4]
                            date = datetime.strptime(dateText, '%Y-%m-%d')
                            deadline = date + timedelta(days=30)
                            text4.insert(INSERT, beforeLend[5])
                            text4.insert(INSERT, deadline.strftime("%Y-%m-%d"))
                            text4.insert(INSERT, '\n')
                        else:
                            mBox.showerror('Error', 'record is not existed!')
                    else:
                        mBox.showerror('Error', 'the people is not existed!')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            elif bName and not pName:
                if bName in bnameList:
                    bNo = ms.ExecQuery(u"SELECT Bno FROM Books WHERE Bname='{}'".format(bName))[0]
                    resListB = []
                    resListBno = ms.ExecQuery("SELECT Bno FROM BookLend")
                    for item in resListBno:
                        resListB.append(item[0])
                    if bNo[0] in resListB:
                        sql = u"SELECT * FROM LendInfo WHERE Bno='{}'".format(bNo[0])
                        res = ms.ExecQuery(sql)
                        text4.delete(1.0, END)
                        for i in range(len(res)):
                            resExtra = res[i]
                            text4.insert(INSERT, '\n')
                            for item in range(5):
                                text4.insert(INSERT, beforeLend[item])
                                text4.insert(INSERT, resExtra[item])
                                text4.insert(INSERT, '\n')
                            dateText = resExtra[4]
                            date = datetime.strptime(dateText, '%Y-%m-%d')
                            deadline = date + timedelta(days=30)
                            text4.insert(INSERT, beforeLend[5])
                            text4.insert(INSERT, deadline.strftime("%Y-%m-%d"))
                            text4.insert(INSERT, '\n')
                    else:
                        mBox.showerror('Error', 'record is not existed!')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            elif pName and not bName:
                if pName in pnameList:
                    pNo = ms.ExecQuery(u"SELECT Pno FROM People WHERE Pname='{}'".format(pName))[0]
                    resListP = []
                    resListPno = ms.ExecQuery("SELECT Pno FROM BookLend")
                    for item in resListPno:
                        resListP.append(item[0])
                    if pNo[0] in resListP:
                        sql = u"SELECT * FROM LendInfo WHERE Pno='{}'".format(pNo[0])
                        res = ms.ExecQuery(sql)
                        text4.delete(1.0, END)
                        for i in range(len(res)):
                            resExtra = res[i]
                            text4.insert(INSERT, '\n')
                            for item in range(5):
                                text4.insert(INSERT, beforeLend[item])
                                text4.insert(INSERT, resExtra[item])
                                text4.insert(INSERT, '\n')
                            dateText = resExtra[4]
                            date = datetime.strptime(dateText, '%Y-%m-%d')
                            deadline = date + timedelta(days=30)
                            text4.insert(INSERT, beforeLend[5])
                            text4.insert(INSERT, deadline.strftime("%Y-%m-%d"))
                            text4.insert(INSERT, '\n')
                    else:
                        mBox.showerror('Error', 'record is not existed!')
                else:
                    mBox.showerror('Error', 'the people is not existed!')
            else:
                mBox.showwarning('Warning', 'choose an option at least!')

        #删除借书记录
        def deleteLendRecord():
            bName = bookNameChosen4.get()
            pName = peopleNameChosen3.get()
            bnameList = []
            answer = mBox.askyesno('WARNING', 'Are u SURE to DELETE?')
            if answer:
                resListBname = ms.ExecQuery("SELECT Bname FROM Books")
                for infoBname in resListBname:
                    bnameList.append(infoBname[0])
                pnameList = []
                resListPname = ms.ExecQuery("SELECT Pname FROM People")
                for infoPname in resListPname:
                    pnameList.append(infoPname[0])
                resListBP = ms.ExecQuery("SELECT Bno,Pno FROM BookLend")
                if bName and pName:
                    if bName in bnameList:
                        if pName in pnameList:
                            bNo = ms.ExecQuery(u"SELECT Bno FROM Books WHERE Bname='{}'".format(bName))[0]
                            pNo = ms.ExecQuery(u"SELECT Pno FROM People WHERE Pname='{}'".format(pName))[0]
                            if (bNo[0], pNo[0]) in resListBP:
                                flag = ms.ExecQuery(u"SELECT Flag FROM BookLend WHERE Bno='{}'".format(bNo[0]))[0]
                                if flag[0] == 0:
                                    remain = ms.ExecQuery(u"SELECT Bremain FROM Depot WHERE Bno='{}'".format(bNo[0]))[0]
                                    sql = u"DELETE FROM BookLend WHERE Pno='{}' AND Bno='{}'".format(pNo[0], bNo[0])
                                    sql1 = u"UPDATE Depot SET Bremain = ({}+1) WHERE Bno='{}'".format(
                                        remain[0], bNo[0])
                                    ms.ExecNonQuery(sql)
                                    ms.ExecNonQuery(sql1)
                                    text4.delete(1.0, END)
                                    mBox.showinfo('Succeed', 'Completed!\n')
                                else:
                                    mBox.showerror('Error','the book has been returned\n and no permission!')
                            else:
                                mBox.showerror('Error', 'record is not existed!')
                        else:
                            mBox.showerror('Error', 'the people is not existed!')
                    else:
                        mBox.showerror('Error', 'the book is not existed!')
                else:
                    mBox.showwarning('Warning', 'both options should be selected!')
            else:
                return

        # 还书
        def returnBooks():
            bName = bookNameChosen5.get()
            pName = peopleNameChosen4.get()
            year = int(spin4.get())
            month = int(spin5.get())
            day = int(spin6.get())
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            pnameList = []
            resListPname = ms.ExecQuery("SELECT Pname FROM People")
            for infoPname in resListPname:
                pnameList.append(infoPname[0])
            resListBP = ms.ExecQuery("SELECT Bno,Pno FROM BookLend")
            resListBP_R = ms.ExecQuery("SELECT Bno,Pno FROM BookReturn")
            if bName and pName:
                if bName in bnameList:
                    if pName in pnameList:
                        bNo = ms.ExecQuery(u"SELECT Bno FROM Books WHERE Bname='{}'".format(bName))[0]
                        pNo = ms.ExecQuery(u"SELECT Pno FROM People WHERE Pname='{}'".format(pName))[0]
                        if (bNo[0], pNo[0])  in resListBP:
                            if (bNo[0], pNo[0]) not in resListBP_R:
                                dateText = '{}/{}/{}'.format(year, month, day)
                                remain = ms.ExecQuery(u"SELECT Bremain FROM Depot WHERE Bno='{}'".format(bNo[0]))[0]
                                sql = u"UPDATE BookLend SET Flag=1 WHERE Bno='{}' AND Pno='{}'".format(bNo[0], pNo[0])
                                sql1 = u"INSERT INTO BookReturn VALUES ('{}','{}','{}')".format(pNo[0], bNo[0], dateText)
                                sql2 = u"UPDATE Depot SET Bremain = ({}+1) WHERE Bno in (SELECT Bno FROM Books WHERE Bname='{}')".format(
                                    remain[0], bName)
                                ms.ExecNonQuery(sql)
                                ms.ExecNonQuery(sql1)
                                ms.ExecNonQuery(sql2)
                                mBox.showinfo('Succeed', 'Completed!\n')
                            else:
                                mBox.showinfo('caution', 'the book has been returned!')
                        else:
                            mBox.showerror('Error', 'lend record is not existed!')
                    else:
                        mBox.showerror('Error', 'the people is not existed!')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            else:
                mBox.showwarning('Warning', 'both options should be selected!')

        # 查询还书记录
        def checkReturnRecord():
            bName = bookNameChosen5.get()
            pName = peopleNameChosen4.get()
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            pnameList = []
            resListPname = ms.ExecQuery("SELECT Pname FROM People")
            for infoPname in resListPname:
                pnameList.append(infoPname[0])
            resListBP_R = ms.ExecQuery("SELECT Bno,Pno FROM BookReturn")
            if bName and pName:
                if bName in bnameList:
                    if pName in pnameList:
                        bNo = ms.ExecQuery(u"SELECT Bno FROM Books WHERE Bname='{}'".format(bName))[0]
                        pNo = ms.ExecQuery(u"SELECT Pno FROM People WHERE Pname='{}'".format(pName))[0]
                        if (bNo[0], pNo[0]) in resListBP_R:
                            sql = u"SELECT * FROM ReturnInfo WHERE Bno='{}' AND Pno='{}'".format(bNo[0], pNo[0])
                            res = ms.ExecQuery(sql)[0]
                            text5.delete(1.0, END)
                            text5.insert(INSERT, '\n')
                            for item in range(5):
                                text5.insert(INSERT, beforeReturn[item])
                                text5.insert(INSERT, res[item])
                                text5.insert(INSERT, '\n')
                        else:
                            mBox.showerror('Error', 'record is not existed!')
                    else:
                        mBox.showerror('Error', 'the people is not existed!')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            elif bName and not pName:
                if bName in bnameList:
                    bNo = ms.ExecQuery(u"SELECT Bno FROM Books WHERE Bname='{}'".format(bName))[0]
                    resListB = []
                    resListBno = ms.ExecQuery("SELECT Bno FROM BookReturn")
                    for item in resListBno:
                        resListB.append(item[0])
                    if bNo[0] in resListB:
                        sql = u"SELECT * FROM ReturnInfo WHERE Bno='{}'".format(bNo[0])
                        res = ms.ExecQuery(sql)
                        text5.delete(1.0, END)
                        for i in range(len(res)):
                            resExtra = res[i]
                            text5.insert(INSERT, '\n')
                            for item in range(5):
                                text5.insert(INSERT, beforeReturn[item])
                                text5.insert(INSERT, resExtra[item])
                                text5.insert(INSERT, '\n')
                    else:
                        mBox.showerror('Error', 'record is not existed!')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            elif pName and not bName:
                if pName in pnameList:
                    pNo = ms.ExecQuery(u"SELECT Pno FROM People WHERE Pname='{}'".format(pName))[0]
                    resListP = []
                    resListPno = ms.ExecQuery("SELECT Pno FROM BookReturn")
                    for item in resListPno:
                        resListP.append(item[0])
                    if pNo[0] in resListP:
                        sql = u"SELECT * FROM ReturnInfo WHERE Pno='{}'".format(pNo[0])
                        res = ms.ExecQuery(sql)
                        text5.delete(1.0, END)
                        for i in range(len(res)):
                            resExtra = res[i]
                            text5.insert(INSERT, '\n')
                            for item in range(5):
                                text5.insert(INSERT, beforeReturn[item])
                                text5.insert(INSERT, resExtra[item])
                                text5.insert(INSERT, '\n')
                    else:
                        mBox.showerror('Error', 'record is not existed!')
                else:
                    mBox.showerror('Error', 'the people is not existed!')
            else:
                mBox.showwarning('Warning', 'choose an option at least!')

        # 删除还书记录
        def deleteReturnRecord():
            bName = bookNameChosen5.get()
            pName = peopleNameChosen4.get()
            bnameList = []
            answer = mBox.askyesno('WARNING', 'Are u SURE to DELETE?')
            if answer:
                resListBname = ms.ExecQuery("SELECT Bname FROM Books")
                for infoBname in resListBname:
                    bnameList.append(infoBname[0])
                pnameList = []
                resListPname = ms.ExecQuery("SELECT Pname FROM People")
                for infoPname in resListPname:
                    pnameList.append(infoPname[0])
                resListBP = ms.ExecQuery("SELECT Bno,Pno FROM BookLend")
                resListBP_R = ms.ExecQuery("SELECT Bno,Pno FROM BookReturn")
                if bName and pName:
                    if bName in bnameList:
                        if pName in pnameList:
                            bNo = ms.ExecQuery(u"SELECT Bno FROM Books WHERE Bname='{}'".format(bName))[0]
                            pNo = ms.ExecQuery(u"SELECT Pno FROM People WHERE Pname='{}'".format(pName))[0]
                            if (bNo[0], pNo[0]) in resListBP:
                                if (bNo[0], pNo[0]) in resListBP_R:
                                    remain = ms.ExecQuery(u"SELECT Bremain FROM Depot WHERE Bno='{}'".format(bNo[0]))[0]
                                    sql = u"DELETE FROM BookReturn WHERE Pno='{}' AND Bno='{}'".format(pNo[0], bNo[0])
                                    sql1 = u"UPDATE Depot SET Bremain = ({}-1) WHERE Bno='{}'".format(
                                        remain[0], bNo[0])
                                    sql2 = u"UPDATE BookLend SET Flag=0 WHERE Pno='{}' AND Bno='{}'".format(pNo[0], bNo[0])
                                    # print(sql)
                                    # print(sql1)
                                    # print(sql2)
                                    ms.ExecNonQuery(sql)
                                    ms.ExecNonQuery(sql1)
                                    ms.ExecNonQuery(sql2)
                                    text5.delete(1.0, END)
                                    mBox.showinfo('Succeed', 'Completed!\n')
                                else:
                                    mBox.showerror('Error', 'return record is not existed!')
                            else:
                                mBox.showerror('Error', 'lend record is not existed!')
                        else:
                            mBox.showerror('Error', 'the people is not existed!')
                    else:
                        mBox.showerror('Error', 'the book is not existed!')
                else:
                    mBox.showwarning('Warning', 'both options should be selected!')
            else:
                return


        # 入库
        def addToDepot():
            bn = bookNameChosen3.get()
            spn = spin.get()
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            # 获取书号列表
            bnoListD = []
            bnoInD = ms.ExecQuery(u"SELECT Bno FROM Depot")
            for item in bnoInD:
                bnoListD.append(item[0])
            if bn:
                if bn in bnameList:
                    sql = u"SELECT Bno FROM Books WHERE Bname='{}'".format(bn)
                    nmbr = ms.ExecQuery(sql)[0]  # get Bno
                    if nmbr[0] not in bnoListD:
                        sql1 = u"INSERT INTO Depot VALUES('{}',{})".format(
                            nmbr[0], spn)
                        ms.ExecNonQuery(sql1)
                        mBox.showinfo('Succeed', 'Completed!')
                    else:
                        mBox.showerror(
                            'Error', 'the book has existed\nselect update button')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            else:
                mBox.showwarning('Warning', 'did not input any book!')

        # 修改库存
        def updateDepot():
            bn = bookNameChosen3.get()
            spn = spin.get()
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            # 获取书号列表
            bnoListD = []
            bnoInD = ms.ExecQuery(u"SELECT Bno FROM Depot")
            for item in bnoInD:
                bnoListD.append(item[0])
            if bn:
                if bn in bnameList:
                    sql = u"SELECT Bno FROM Books WHERE Bname='{}'".format(bn)
                    nmbr = ms.ExecQuery(sql)[0]  # get Bno
                    if nmbr[0] in bnoListD:
                        sql1 = u"UPDATE Depot SET Bremain={} WHERE Bno='{}'".format(
                            spn, nmbr[0])
                        ms.ExecNonQuery(sql1)
                        mBox.showinfo('Succeed', 'Completed!')
                    else:
                        mBox.showerror('Error', 'the table has no records!')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            else:
                mBox.showwarning('Warning', 'did not input any book!')

        # 查询库存
        def checkDepot():
            bn = bookNameChosen3.get()
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            # 获取书号列表
            bnoListD = []
            bnoInD = ms.ExecQuery(u"SELECT Bno FROM Depot")
            for item in bnoInD:
                bnoListD.append(item[0])
            if bn:
                if bn in bnameList:
                    sql = u"SELECT Bno FROM Books WHERE Bname='{}'".format(bn)
                    nmbr = ms.ExecQuery(sql)[0]  # get Bno
                    if nmbr[0] in bnoListD:
                        sql1 = u"SELECT * FROM Depot WHERE Bno=(SELECT Bno FROM Books WHERE Bname='{}')".format(
                            bn)
                        res = ms.ExecQuery(sql1)[0]
                        text2.delete(1.0, END)
                        text2.insert(INSERT, '书名:')
                        text2.insert(INSERT, bn + '\n')
                        text2.insert(INSERT, '书号:')
                        text2.insert(INSERT, res[0] + '\n')
                        text2.insert(INSERT, '库存:')
                        text2.insert(INSERT, str(res[1]) + '\n')
                    else:
                        mBox.showerror('Error', 'the table has no records!')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            else:
                mBox.showwarning('Warning', 'did not input any book!')

        # 清空库存
        def clearDepot():
            bn = bookNameChosen3.get()
            bnameList = []
            resListBname = ms.ExecQuery("SELECT Bname FROM Books")
            for infoBname in resListBname:
                bnameList.append(infoBname[0])
            # 获取书号列表
            bnoListD = []
            bnoInD = ms.ExecQuery(u"SELECT Bno FROM Depot")
            for item in bnoInD:
                bnoListD.append(item[0])
            if bn:
                if bn in bnameList:
                    sql = u"SELECT Bno FROM Books WHERE Bname='{}'".format(bn)
                    nmbr = ms.ExecQuery(sql)[0]  # get Bno
                    if nmbr[0] in bnoListD:
                        answer = mBox.askyesno(
                            'WARNING', 'ARE U SURE TO DELETE?')
                        if answer:
                            sql1 = u"DELETE FROM Depot WHERE Bno=(SELECT Bno FROM Books WHERE Bname='{}')".format(
                                bn)
                            ms.ExecNonQuery(sql1)
                            mBox.showinfo('Succeed', 'Completed!')
                        else:
                            mBox.showinfo('okay', 'let\'s go on')
                    else:
                        mBox.showerror('Error', 'the table has no records!')
                else:
                    mBox.showerror('Error', 'the book is not existed!')
            else:
                mBox.showwarning('Warning', 'did not input any book!')

        #按种类模糊查找
        def FuzzySearch_type():
            try:
                type_ = ent14.get()
                btypeList = []
                resListBtype = ms.ExecQuery("SELECT Btype FROM Category")
                for item in resListBtype:
                    btypeList.append(item[0])
                if type_:
                    flag = 0
                    for i in range(len(btypeList)):
                        if type_ in btypeList[i]:
                            flag = 1
                            break
                        else:
                            flag = 0
                    if flag:
                        sql = u"EXEC FuzzySearch_type '{}'".format(type_)
                        resList = ms.ExecQuery(sql)
                        text6.delete(1.0, END)
                        for item in range(len(resList)):
                            res = resList[item]
                            text6.insert(INSERT, '\n')
                            for item in range(7):
                                text6.insert(INSERT, before[item])
                                text6.insert(INSERT, res[item])
                                text6.insert(INSERT, '\n')
                    else:
                        mBox.showerror('Error', 'the book is not existed!')
                else:
                    mBox.showwarning('Warning', 'did not input any type!')
            except BaseException:
                text6.delete(1.0, END)
                text6.insert(INSERT, 'System crashed...Please retry')
            return

        #按作者模糊查找
        def FuzzySearch_name():
            try:
                author = ent15.get()
                bauthorList = []
                resListBauthor = ms.ExecQuery("SELECT Bauthor FROM Books")
                for item in resListBauthor:
                    bauthorList.append(item[0])
                if author:
                    flag = 0
                    for i in range(len(bauthorList)):
                        if author in bauthorList[i]:
                            flag = 1
                            break
                        else:
                            flag = 0
                    if flag:
                        sql = u"EXEC FuzzySearch_name '{}'".format(author)
                        resList = ms.ExecQuery(sql)
                        text6.delete(1.0, END)
                        for item in range(len(resList)):
                            res = resList[item]
                            text6.insert(INSERT, '\n')
                            for item in range(7):
                                text6.insert(INSERT, before[item])
                                text6.insert(INSERT, res[item])
                                text6.insert(INSERT, '\n')
                    else:
                        mBox.showerror('Error', 'the book is not existed!')
                else:
                    mBox.showwarning('Warning', 'did not input any author!')
            except BaseException:
                text6.delete(1.0, END)
                text6.insert(INSERT, 'System crashed...Please retry')
            return

        #按书名模糊查找
        def FuzzySearch_name_onBooks():
            try:
                name = ent16.get()
                bnameList = []
                resListBname = ms.ExecQuery("SELECT Bname FROM Books")
                for item in resListBname:
                    bnameList.append(item[0])
                if name:
                    flag = 0
                    for i in range(len(bnameList)):
                        if name in bnameList[i]:
                            flag = 1
                            break
                        else:
                            flag = 0
                    if flag:
                        sql = u"EXEC FuzzySearch_name_onBooks '{}'".format(name)
                        resList = ms.ExecQuery(sql)
                        text6.delete(1.0, END)
                        for item in range(len(resList)):
                            res = resList[item]
                            text6.insert(INSERT, '\n')
                            for item in range(7):
                                text6.insert(INSERT, before[item])
                                text6.insert(INSERT, res[item])
                                text6.insert(INSERT, '\n')
                    else:
                        mBox.showerror('Error', 'the book is not existed!')
                else:
                    mBox.showwarning('Warning', 'did not input any book!')
            except BaseException:
                text6.delete(1.0, END)
                text6.insert(INSERT, 'System crashed...Please retry')
            return

        #修改指定书籍类别
        def category_update():
            try:
                type_ = typeChosen1.get()
                name = bookNameChosen6.get()
                bnameList = []
                resListBname = ms.ExecQuery("SELECT Bname FROM Books")
                for item in resListBname:
                    bnameList.append(item[0])
                if name:
                    if name in bnameList:
                        sql = u"EXEC category_update '{}','{}'".format(name,type_)
                        ms.ExecNonQuery(sql)
                        mBox.showinfo('Succeed', 'Completed!')
                    else:
                        mBox.showerror('Error', 'the book is not existed!')
                else:
                    mBox.showwarning('Warning', 'did not input any book!')
            except BaseException:
                text6.delete(1.0, END)
                text6.insert(INSERT, 'System crashed...Please retry')
            return


        # 退出函数

        def _quit():
            root.quit()
            root.destroy()
            exit()

        # ===========================================================
        # 总窗口

        root = Tk()
        root.title('Library')
        root.geometry('+400+100')
        root.geometry('460x490')
        root.iconbitmap(r'C:\tank.ico')
        # file menu
        menuBar = Menu(root)
        root.config(menu=menuBar)
        fileMenu = Menu(menuBar, tearoff=0)
        fileMenu.add_command(label='New')
        fileMenu.add_separator()
        fileMenu.add_command(label='Exit', command=_quit)
        menuBar.add_cascade(label='File', menu=fileMenu)
        # help menu
        helpMenu = Menu(menuBar, tearoff=0)
        helpMenu.add_command(label="About", command=msgBoxInfoAbout)
        helpMenu.add_separator()
        helpMenu.add_command(label="Feedback", command=msgBoxFeedback)
        menuBar.add_cascade(label="Help", menu=helpMenu)
        # all tab
        tabControl = ttk.Notebook(root)
        tab1 = ttk.LabelFrame(
            tabControl,
            text='bookInfo',
            width=500,
            height=400)
        tabControl.add(tab1, text='查书')
        tab2 = ttk.LabelFrame(
            tabControl,
            text='addBook',
            width=500,
            height=400)
        tabControl.add(tab2, text='购书')
        tab4 = ttk.LabelFrame(tabControl, text='delete', width=500, height=400)
        tabControl.add(tab4, text='删除')
        tab5 = ttk.LabelFrame(tabControl, text='modify', width=500, height=400)
        tabControl.add(tab5, text='修改')
        tab3 = ttk.LabelFrame(
            tabControl,
            text='peopleInfo',
            width=500,
            height=400)
        tabControl.add(tab3, text='用户')
        tab6 = ttk.LabelFrame(tabControl, text='lend', width=500, height=400)
        tabControl.add(tab6, text='借书')
        tab7 = ttk.LabelFrame(tabControl, text='return', width=500, height=400)
        tabControl.add(tab7, text='还书')
        tab8 = ttk.LabelFrame(tabControl, text='depot', width=500, height=400)
        tabControl.add(tab8, text='库存')
        tab9 = ttk.LabelFrame(tabControl, text='type', width=500, height=400)
        tabControl.add(tab9, text='类别')
        tabControl.pack(expand=1, fill='both')

        # ===========================================================

        # tab 1
        # labelframe
        labelsFrame1 = ttk.LabelFrame(tab1, text='操作栏')
        labelsFrame1.grid(row=3, column=0, columnspan=4)
        labelsFrame3 = ttk.LabelFrame(tab1, text='结果')
        labelsFrame3.grid(row=4, column=0, columnspan=4)

        # label
        label1 = Label(
            labelsFrame1,
            text='书号推荐:',
            fg='red',
            width=10,
            height=1)
        label1.grid(row=0, column=0, sticky=W)
        label3 = Label(
            labelsFrame1,
            text='书名推荐:',
            fg='blue',
            width=0,
            height=1)
        label3.grid(row=0, column=1, sticky=E)

        # combobox
        book = StringVar()
        bookNumChosen = ttk.Combobox(labelsFrame1, width=15, textvariable=book)
        bnoList = []
        ms = MSSQL(host="localhost", user="sa", pwd="666666", db="LibraryX")
        resListBno = ms.ExecQuery("SELECT Bno FROM Books")
        for infoBno in resListBno:
            bnoList.append(infoBno[0])
        bnoTuple = tuple(bnoList)
        bookNumChosen['values'] = bnoTuple
        bookNumChosen.grid(row=1, column=0, sticky=W, padx=10)
        bookNumChosen.current()

        book1 = StringVar()
        bookNameChosen = ttk.Combobox(
            labelsFrame1, width=15, textvariable=book1)
        bnameList = []
        resListBname = ms.ExecQuery("SELECT Bname FROM Books")
        for infoBname in resListBname:
            bnameList.append(infoBname[0])
        bnameTuple = tuple(bnameList)
        bookNameChosen['values'] = bnameTuple
        bookNameChosen.grid(row=1, column=1, sticky=W)
        bookNameChosen.current()

        # button
        button1 = Button(
            labelsFrame1,
            text='书号查询',
            bg='palegreen',
            bd=2,
            command=getBookByBno)
        button1.grid(row=2, column=0, padx=10, pady=10, sticky=W)
        button2 = Button(
            labelsFrame1,
            text='书名查询',
            bg='palegreen',
            bd=2,
            command=getBookByBname)
        button2.grid(row=2, column=1, pady=10, sticky=E)
        # scroll text
        scrollW = 60
        scrollH = 15
        text = scrolledtext.ScrolledText(
            labelsFrame3, width=scrollW, height=scrollH, wrap=WORD)
        text.grid(column=0, columnspan=3, padx=5, pady=5, sticky='E')

        # ===========================================================

        # tab 2
        # label
        label4 = Label(
            tab2,
            text='Go get the book!',
            fg='red',
            width=20,
            height=1)
        label4.grid(row=0, column=0, sticky=W)
        labelText2 = [
            '--书号--:',
            '--书名--:',
            '--作者--:',
            '--RMB--:',
            '--出版社--:',
            '--简介--:',
            '--类别--:']
        for rw in range(7):
            label = Label(
                tab2,
                text=labelText2[rw],
                fg='green',
                width=10,
                height=1)
            label.grid(row=rw + 1, column=0, sticky=E)

        # entry
        ent1 = Entry(tab2, width=37, bd=2, insertbackground='green')
        ent1.grid(row=1, column=1, pady=2, sticky=W)
        ent2 = Entry(tab2, width=37, bd=2, insertbackground='green')
        ent2.grid(row=2, column=1, pady=2, sticky=W)
        ent3 = Entry(tab2, width=37, bd=2, insertbackground='green')
        ent3.grid(row=3, column=1, pady=2, sticky=W)
        ent4 = Entry(tab2, width=37, bd=2, insertbackground='green')
        ent4.grid(row=4, column=1, pady=2, sticky=W)
        ent5 = Entry(tab2, width=37, bd=2, insertbackground='green')
        ent5.grid(row=5, column=1, pady=2, sticky=W)
        ent6 = Entry(tab2, width=37, bd=2, insertbackground='green')
        ent6.grid(row=6, column=1, pady=2, sticky=W)

        # combobox
        type_ = StringVar()
        typeChosen = ttk.Combobox(tab2, width=15, textvariable=type_)
        typeChosen['values'] = category
        typeChosen.grid(row=7, column=1, sticky=W, pady=2)
        typeChosen.current()

        # button
        button3 = Button(
            tab2,
            text='PUT DOWN MONEY',
            bg='gold',
            command=addBooks)
        button3.grid(row=9, column=1, sticky=E)

        # ===========================================================

        # tab3
        # labelframe
        labelsFrame4 = ttk.LabelFrame(tab3, text='开户')
        labelsFrame4.grid(row=0, column=0, columnspan=4, sticky=W)
        labelsFrame5 = ttk.LabelFrame(tab3, text='操作栏')
        labelsFrame5.grid(row=2, column=0, columnspan=4, sticky=W)
        labelsFrame6 = ttk.LabelFrame(labelsFrame5, text='结果')
        labelsFrame6.grid(row=1, column=0, columnspan=4)
        # label
        peopleInfo = ('编号:', '姓名:', '充值:', '公司:', '职位:')
        Label(labelsFrame4, text='新用户必填:', fg='red', width=6,
              padx=10).grid(
            row=0, column=0, sticky=W)
        Label(labelsFrame4, text=peopleInfo[0], fg='royalblue', width=4,
              padx=10).grid(
            row=1, column=0, sticky=E)
        Label(labelsFrame4, text=peopleInfo[1], fg='royalblue', width=4,
              padx=10).grid(
            row=1, column=3, sticky=E)
        Label(labelsFrame4, text=peopleInfo[2], fg='royalblue', width=4,
              padx=10).grid(
            row=1, column=5, sticky=E)
        Label(labelsFrame4, text=peopleInfo[3], fg='royalblue', width=4,
              padx=10).grid(
            row=2, column=0, sticky=E)
        Label(labelsFrame4, text=peopleInfo[4], fg='royalblue', width=4,
              padx=10).grid(
            row=2, column=3, sticky=E)
        Label(labelsFrame5, text='选择用户:', fg='red', width=8, height=1,
              padx=10, pady=5).grid(
            row=0, column=1, sticky=W)
        # entry
        ent9 = Entry(labelsFrame4, width=10, bd=2, insertbackground='green')
        ent9.grid(row=1, column=1, pady=2, sticky=W)
        ent10 = Entry(labelsFrame4, width=10, bd=2, insertbackground='green')
        ent10.grid(row=1, column=4, pady=2, sticky=W)
        ent11 = Entry(labelsFrame4, width=10, bd=2, insertbackground='green')
        ent11.grid(row=1, column=6, pady=2, sticky=W)
        ent12 = Entry(labelsFrame4, width=10, bd=2, insertbackground='green')
        ent12.grid(row=2, column=1, pady=2, sticky=W)
        ent13 = Entry(labelsFrame4, width=10, bd=2, insertbackground='green')
        ent13.grid(row=2, column=4, pady=2, sticky=W)
        # button
        button11 = Button(
            labelsFrame4,
            text='创建用户',
            bg='palegreen',
            width=10,
            command=addPeople)
        button11.grid(row=2, column=6, sticky=E, pady=2)
        button12 = Button(
            labelsFrame5,
            text='查询',
            bg='palegreen',
            width=10,
            command=checkPeople)
        button12.grid(row=2, column=0, sticky=W, pady=5)
        button13 = Button(
            labelsFrame5,
            text='删除',
            bg='tomato',
            width=10,
            command=deletePeople)
        button13.grid(row=2, column=3, pady=5)
        # combobox
        people2 = StringVar()
        peopleNameChosen2 = ttk.Combobox(
            labelsFrame5, width=15, textvariable=people2)
        pnameList = []
        resListPname = ms.ExecQuery("SELECT Pname FROM People")
        for infoPname in resListPname:
            pnameList.append(infoPname[0])
        pnameTuple = tuple(pnameList)
        peopleNameChosen2['values'] = pnameTuple
        peopleNameChosen2.grid(row=0, column=2, sticky=W)
        peopleNameChosen2.current()
        # scrolltext
        text3 = scrolledtext.ScrolledText(
            labelsFrame6, width=scrollW, height=13, wrap=WORD)
        text3.grid(column=0, columnspan=3, padx=5, pady=5, sticky='E')

        # ===========================================================

        # tab4
        labelsFrame7 = ttk.LabelFrame(tab4, text='结果')
        labelsFrame7.grid(row=1, column=0, columnspan=4)
        # label
        label12 = Label(tab4, text='选择删除:', fg='red', width=10, height=1)
        label12.grid(row=0, column=0, sticky=E)
        # combobox
        book2 = tk.StringVar()
        checkBookNameChosen = ttk.Combobox(tab4, width=15, textvariable=book2)
        checkBookNameChosen['values'] = bnameTuple
        checkBookNameChosen.grid(row=0, column=1, sticky=W)
        checkBookNameChosen.current()
        # button
        button4 = Button(
            tab4,
            text='细节',
            bg='palegreen',
            width=10,
            command=checkBooks)
        button4.grid(row=2, column=0, padx=10, pady=10)
        button5 = Button(
            tab4,
            text='删除',
            bg='tomato',
            width=10,
            command=deleteBooks)
        button5.grid(row=2, column=2, pady=10, sticky=E)
        # scroll text
        text1 = scrolledtext.ScrolledText(
            labelsFrame7, width=scrollW, height=scrollH, wrap=WORD)
        text1.grid(column=0, columnspan=2, padx=5, pady=5, sticky='E')

        # ===========================================================

        # tab5
        # labelframe
        labelsFrame8 = ttk.LabelFrame(tab5, text='选择')
        labelsFrame8.grid(row=2, column=0, columnspan=4)
        # label
        label13 = Label(tab5, text='先选择!', fg='red', width=6, height=1)
        label13.grid(row=0, column=0, sticky=W)
        # checkbuttons
        chVar_P = tk.IntVar()
        check_P = tk.Checkbutton(
            tab5, text="用户库", fg='purple', variable=chVar_P)
        check_P.deselect()
        check_P.grid(row=1, column=1, sticky=tk.W)

        chVar_B = tk.IntVar()
        check_B = tk.Checkbutton(
            tab5, text="图书库", fg='orange', variable=chVar_B)
        check_B.deselect()
        check_B.grid(row=1, column=0, sticky=tk.W)

        chVar_D = tk.IntVar()
        check3 = tk.Checkbutton(
            tab5,
            text="库存",
            variable=chVar_D,
            state='disabled')
        check3.deselect()
        check3.grid(row=1, column=2, sticky=tk.W)

        bookItem = ['书号', '书名', '作者', '价格', '出版社', '简介']
        peopleItem = ['编号', '姓名', '余额', '单位', '职位']

        # create Radiobuttons using one variable
        radVar_B = tk.IntVar()
        radVar_P = tk.IntVar()
        # Selecting a non-existing index value for radVar
        radVar_B.set(99)
        radVar_P.set(99)

        # Radiobuttons
        curRad_B0 = tk.Radiobutton(
            tab5,
            text=bookItem[0],
            fg='orange',
            variable=radVar_B,
            value=0)
        curRad_B0.grid(row=3, column=0, sticky=tk.W)
        curRad_B1 = tk.Radiobutton(
            tab5,
            text=bookItem[1],
            fg='orange',
            variable=radVar_B,
            value=1)
        curRad_B1.grid(row=3, column=1, sticky=tk.W)
        curRad_B2 = tk.Radiobutton(
            tab5,
            text=bookItem[2],
            fg='orange',
            variable=radVar_B,
            value=2)
        curRad_B2.grid(row=3, column=2, sticky=tk.W)
        curRad_B3 = tk.Radiobutton(
            tab5,
            text=bookItem[3],
            fg='orange',
            variable=radVar_B,
            value=3)
        curRad_B3.grid(row=3, column=3, sticky=tk.W)
        curRad_B4 = tk.Radiobutton(
            tab5,
            text=bookItem[4],
            fg='orange',
            variable=radVar_B,
            value=4)
        curRad_B4.grid(row=3, column=4, sticky=tk.W)
        curRad_B5 = tk.Radiobutton(
            tab5,
            text=bookItem[5],
            fg='orange',
            variable=radVar_B,
            value=5)
        curRad_B5.grid(row=3, column=5, sticky=tk.W)

        curRad_P0 = tk.Radiobutton(
            tab5,
            text=peopleItem[0],
            fg='purple',
            variable=radVar_P,
            value=0)
        curRad_P0.grid(row=4, column=0, sticky=tk.W)
        curRad_P1 = tk.Radiobutton(
            tab5,
            text=peopleItem[1],
            fg='purple',
            variable=radVar_P,
            value=1)
        curRad_P1.grid(row=4, column=1, sticky=tk.W)
        curRad_P2 = tk.Radiobutton(
            tab5,
            text=peopleItem[2],
            fg='purple',
            variable=radVar_P,
            value=2)
        curRad_P2.grid(row=4, column=2, sticky=tk.W)
        curRad_P3 = tk.Radiobutton(
            tab5,
            text=peopleItem[3],
            fg='purple',
            variable=radVar_P,
            value=3)
        curRad_P3.grid(row=4, column=3, sticky=tk.W)
        curRad_P4 = tk.Radiobutton(
            tab5,
            text=peopleItem[4],
            fg='purple',
            variable=radVar_P,
            value=4)
        curRad_P4.grid(row=4, column=4, sticky=tk.W)

        # GUI Callback function
        def checkCallback(*ignoredArgs):
            # only enable one checkbutton
            if chVar_P.get():
                check_B.configure(state='disabled')
                curRad_B0.config(state='disabled')
                curRad_B1.config(state='disabled')
                curRad_B2.config(state='disabled')
                curRad_B3.config(state='disabled')
                curRad_B4.config(state='disabled')
                curRad_B5.config(state='disabled')
            else:
                check_B.configure(state='normal')
                curRad_B0.config(state='normal')
                curRad_B1.config(state='normal')
                curRad_B2.config(state='normal')
                curRad_B3.config(state='normal')
                curRad_B4.config(state='normal')
                curRad_B5.config(state='normal')
            if chVar_B.get():
                check_P.configure(state='disabled')
                curRad_P0.config(state='disabled')
                curRad_P1.config(state='disabled')
                curRad_P2.config(state='disabled')
                curRad_P3.config(state='disabled')
                curRad_P4.config(state='disabled')
            else:
                check_P.configure(state='normal')
                curRad_P0.config(state='normal')
                curRad_P1.config(state='normal')
                curRad_P2.config(state='normal')
                curRad_P3.config(state='normal')
                curRad_P4.config(state='normal')

        # trace the state of the two checkbuttons
        chVar_P.trace('w', lambda unused0, unused1, unused2: checkCallback())
        chVar_B.trace('w', lambda unused0, unused1, unused2: checkCallback())
        # label
        Label(labelsFrame8, text='选择图书:', fg='red', width=6, height=1).grid(
            row=0, column=0, sticky=W)
        Label(labelsFrame8, text='选择用户:', fg='blue', width=6, height=1).grid(
            row=0, column=1, padx=10, sticky=W)
        Label(tab5, text='修改为:', fg='red', width=6, height=1).grid(
            row=5, column=0, sticky=W)
        # combobox
        book2 = StringVar()
        bookNameChosen2 = ttk.Combobox(
            labelsFrame8, width=15, textvariable=book2)
        bookNameChosen2['values'] = bnameTuple
        bookNameChosen2.grid(row=1, column=0, sticky=W)
        bookNameChosen2.current()

        people = StringVar()
        peopleNameChosen = ttk.Combobox(
            labelsFrame8, width=15, textvariable=people)
        peopleNameChosen['values'] = pnameTuple
        peopleNameChosen.grid(row=1, column=1, padx=10, sticky=W)
        peopleNameChosen.current()
        # entry
        ent7 = Entry(
            tab5,
            width=8,
            bd=2,
            insertbackground='red')
        ent7.grid(
            row=5,
            column=1,
            sticky=W)
        # button
        button6 = Button(
            tab5,
            text='修改',
            bg='palegreen',
            width=10,
            bd=2,
            command=updateBooks)
        button6.grid(row=6, column=5, sticky=W)

        # ===========================================================

        # tab6
        # labelframe
        labelsFrame9 = ttk.LabelFrame(tab6, text='选择栏')
        labelsFrame9.grid(row=0, column=0, columnspan=2)
        labelsFrame10 = ttk.LabelFrame(tab6, text='时间')
        labelsFrame10.grid(row=1, column=0, columnspan=2)
        labelsFrame11 = ttk.LabelFrame(tab6, text='结果')
        labelsFrame11.grid(row=2, column=0, columnspan=2)
        labelsFrame12 = ttk.LabelFrame(tab6, text='操作栏')
        labelsFrame12.grid(row=3, column=0, columnspan=2)
        # label
        Label(labelsFrame9, text='选择图书:', fg='red', width=6, height=1).grid(
            row=0, column=0, sticky=W)
        Label(labelsFrame9, text='选择用户:', fg='blue', width=6, height=1).grid(
            row=0, column=1, padx=10, sticky=E)
        Label(labelsFrame10, text='年', fg='orangered', width=1, height=1).grid(
            row=0, column=1, padx=10, sticky=W)
        Label(labelsFrame10, text='月', fg='orangered', width=1, height=1).grid(
            row=0, column=3, padx=10, sticky=W)
        Label(labelsFrame10, text='日', fg='orangered', width=1, height=1).grid(
            row=0, column=5, padx=10, sticky=W)
        # combobox
        book4 = StringVar()
        bookNameChosen4 = ttk.Combobox(
            labelsFrame9, width=15, textvariable=book4)
        bookNameChosen4['values'] = bnameTuple
        bookNameChosen4.grid(row=1, column=0, sticky=W, padx=10)
        bookNameChosen4.current()

        people3 = StringVar()
        peopleNameChosen3 = ttk.Combobox(
            labelsFrame9, width=15, textvariable=people3)
        peopleNameChosen3['values'] = pnameTuple
        peopleNameChosen3.grid(row=1, column=1, padx=10, sticky=W)
        peopleNameChosen3.current()
        # spin box
        spin1 = Spinbox(labelsFrame10, from_=2010, width=8, to=2030, bd=2)
        spin1.grid(row=0, column=0, sticky=W, padx=10, pady=10)
        spin2 = Spinbox(labelsFrame10, from_=1, width=8, to=12, bd=2)
        spin2.grid(row=0, column=2, sticky=W, padx=10, pady=10)
        spin3 = Spinbox(labelsFrame10, from_=1, width=8, to=31, bd=2)
        spin3.grid(row=0, column=4, sticky=W, padx=10, pady=10)
        #button
        button14 = Button(
            labelsFrame12,
            text='借书',
            bg='blueviolet',
            width=10,
            command=lendBooks)
        button14.grid(row=0, column=0, sticky=W, padx=10)
        button15 = Button(
            labelsFrame12,
            text='记录',
            bg='darkorange',
            width=10,
            command=checkLendRecord)
        button15.grid(row=0, column=1, sticky=W, padx=10)
        button16 = Button(
            labelsFrame12,
            text='清除',
            bg='tomato',
            width=10,
            command=deleteLendRecord)
        button16.grid(row=0, column=2, sticky=W, padx=10)
        #scrolltext
        text4 = scrolledtext.ScrolledText(
            labelsFrame11, width=scrollW, height=scrollH, wrap=WORD)
        text4.grid(column=0, columnspan=3, padx=5, pady=5, sticky='E')

        # ===========================================================

        # tab7
        # labelframe
        labelsFrame13 = ttk.LabelFrame(tab7, text='选择栏')
        labelsFrame13.grid(row=0, column=0, columnspan=2)
        labelsFrame14 = ttk.LabelFrame(tab7, text='时间')
        labelsFrame14.grid(row=1, column=0, columnspan=2)
        labelsFrame15 = ttk.LabelFrame(tab7, text='结果')
        labelsFrame15.grid(row=2, column=0, columnspan=2)
        labelsFrame16 = ttk.LabelFrame(tab7, text='操作栏')
        labelsFrame16.grid(row=3, column=0, columnspan=2)
        # label
        Label(labelsFrame13, text='选择图书:', fg='blue', width=6, height=1).grid(
            row=0, column=0, sticky=W)
        Label(labelsFrame13, text='选择用户:', fg='red', width=6, height=1).grid(
            row=0, column=1, padx=10, sticky=E)
        Label(labelsFrame14, text='年', fg='blueviolet', width=1, height=1).grid(
            row=0, column=1, padx=10, sticky=W)
        Label(labelsFrame14, text='月', fg='blueviolet', width=1, height=1).grid(
            row=0, column=3, padx=10, sticky=W)
        Label(labelsFrame14, text='日', fg='blueviolet', width=1, height=1).grid(
            row=0, column=5, padx=10, sticky=W)
        # combobox
        book5 = StringVar()
        bookNameChosen5 = ttk.Combobox(
            labelsFrame13, width=15, textvariable=book5)
        bookNameChosen5['values'] = bnameTuple
        bookNameChosen5.grid(row=1, column=0, sticky=W, padx=10)
        bookNameChosen5.current()

        people4 = StringVar()
        peopleNameChosen4 = ttk.Combobox(
            labelsFrame13, width=15, textvariable=people4)
        peopleNameChosen4['values'] = pnameTuple
        peopleNameChosen4.grid(row=1, column=1, padx=10, sticky=W)
        peopleNameChosen4.current()
        # spin box
        spin4 = Spinbox(labelsFrame14, from_=2010, width=8, to=2030, bd=2)
        spin4.grid(row=0, column=0, sticky=W, padx=10, pady=10)
        spin5 = Spinbox(labelsFrame14, from_=1, width=8, to=12, bd=2)
        spin5.grid(row=0, column=2, sticky=W, padx=10, pady=10)
        spin6 = Spinbox(labelsFrame14, from_=1, width=8, to=31, bd=2)
        spin6.grid(row=0, column=4, sticky=W, padx=10, pady=10)
        # button
        button17 = Button(
            labelsFrame16,
            text='还书',
            bg='blueviolet',
            width=10,
            command=returnBooks)
        button17.grid(row=0, column=0, sticky=W, padx=10)
        button18 = Button(
            labelsFrame16,
            text='记录',
            bg='darkorange',
            width=10,
            command=checkReturnRecord)
        button18.grid(row=0, column=1, sticky=W, padx=10)
        button19 = Button(
            labelsFrame16,
            text='清除',
            bg='tomato',
            width=10,
            command=deleteReturnRecord)
        button19.grid(row=0, column=2, sticky=W, padx=10)
        # scrolltext
        text5 = scrolledtext.ScrolledText(
            labelsFrame15, width=scrollW, height=scrollH, wrap=WORD)
        text5.grid(column=0, columnspan=3, padx=5, pady=5, sticky='E')

        # ===========================================================

        # tab8
        # labelframe
        labelsFrame = ttk.LabelFrame(tab8, text='操作栏')
        labelsFrame.grid(row=0, column=0, columnspan=2)
        labelsFrame2 = ttk.LabelFrame(tab8, text='结果')
        labelsFrame2.grid(row=1, column=0, columnspan=4)
        # combobox
        book3 = StringVar()
        bookNameChosen3 = ttk.Combobox(labelsFrame, width=15, textvariable=book3)
        bookNameChosen3['values'] = bnameTuple
        bookNameChosen3.grid(row=1, columnspan=6, sticky=W, padx=10)
        bookNameChosen3.current()
        # label
        Label(labelsFrame, text='输入书名:', fg='red', width=8, height=1,
              padx=10).grid(
            row=0, column=0, sticky=W)
        Label(labelsFrame, text='选择本数:', fg='red', width=8, height=1,
              padx=10).grid(
            row=0, column=3, sticky=W)
        # spin box
        spin = Spinbox(labelsFrame, from_=0, width=8, to=100, bd=2)
        spin.grid(row=1, column=3, sticky=W, padx=10, pady=10)
        # button
        button7 = Button(
            labelsFrame,
            text='入库',
            bg='palegreen',
            width=10,
            command=addToDepot)
        button7.grid(row=2, column=0, sticky=W, padx=10, pady=10)
        button8 = Button(
            labelsFrame,
            text='修改库存',
            bg='palegreen',
            width=10,
            command=updateDepot)
        button8.grid(row=2, column=1, sticky=W, padx=10, pady=10)
        button9 = Button(
            labelsFrame,
            text='查询库存',
            bg='palegreen',
            width=10,
            command=checkDepot)
        button9.grid(row=2, column=2, sticky=W, padx=10, pady=10)
        button10 = Button(
            labelsFrame,
            text='清空库存',
            bg='tomato',
            width=10,
            command=clearDepot)
        button10.grid(row=2, column=3, sticky=W, padx=10, pady=10)
        # scroll text
        text2 = scrolledtext.ScrolledText(
            labelsFrame2, width=scrollW, height=scrollH, wrap=WORD)
        text2.grid(column=0, columnspan=3, padx=5, pady=5, sticky='E')

        # ===========================================================

        # tab9
        # labelframe
        labelsFrame17 = ttk.LabelFrame(tab9, text='按种类模糊查找,限制长度2')
        labelsFrame17.grid(row=0, column=0, columnspan=2)
        labelsFrame18 = ttk.LabelFrame(tab9, text='按作者模糊查找,限制长度4')
        labelsFrame18.grid(row=1, column=0, columnspan=2)
        labelsFrame19 = ttk.LabelFrame(tab9, text='按书名模糊查找,限制长度4')
        labelsFrame19.grid(row=2, column=0, columnspan=2)
        labelsFrame20 = ttk.LabelFrame(tab9, text='修改指定书籍类别,限定长度4')
        labelsFrame20.grid(row=3, column=0, columnspan=2)
        labelsFrame21 = ttk.LabelFrame(tab9, text='结果')
        labelsFrame21.grid(row=4, column=0, columnspan=2)
        # entry
        ent14 = Entry(labelsFrame17, width=10, bd=2, insertbackground='green')
        ent14.grid(row=0, column=0, pady=2, sticky=W)
        ent15 = Entry(labelsFrame18, width=10, bd=2, insertbackground='green')
        ent15.grid(row=0, column=0, pady=2, sticky=W)
        ent16 = Entry(labelsFrame19, width=10, bd=2, insertbackground='green')
        ent16.grid(row=0, column=0, pady=2, sticky=W)
        # combobox
        book6 = StringVar()
        bookNameChosen6 = ttk.Combobox(labelsFrame20, width=15, textvariable=book6)
        bookNameChosen6['values'] = bnameTuple
        bookNameChosen6.grid(row=0, column=0, sticky=W, padx=10)
        bookNameChosen6.current()

        type1 = StringVar()
        typeChosen1 = ttk.Combobox(labelsFrame20, width=15, textvariable=type1)
        typeChosen1['values'] = category
        typeChosen1.grid(row=0, column=1, sticky=W, pady=2)
        typeChosen1.current()
        # button
        button20 = Button(
            labelsFrame17,
            text='查询',
            bg='darkorange',
            width=10,
            command=FuzzySearch_type)
        button20.grid(row=0, column=1, sticky=W, padx=10)
        button21 = Button(
            labelsFrame18,
            text='查询',
            bg='palegreen',
            width=10,
            command=FuzzySearch_name)
        button21.grid(row=0, column=1, sticky=W, padx=10)
        button22 = Button(
            labelsFrame19,
            text='查询',
            bg='blueviolet',
            width=10,
            command=FuzzySearch_name_onBooks)
        button22.grid(row=0, column=1, sticky=W, padx=10)
        button23 = Button(
            labelsFrame20,
            text='修改',
            bg='tomato',
            width=10,
            command=category_update)
        button23.grid(row=0, column=2, sticky=W, padx=10)
        # scrolltext
        text6 = scrolledtext.ScrolledText(
            labelsFrame21, width=scrollW, height=10, wrap=WORD)
        text6.grid(column=0, columnspan=3, padx=5, pady=5, sticky='E')



        # ===========================================================

        # tip
        createToolTip(label1, 'this is a label!')
        createToolTip(label3, 'this is a label!')
        createToolTip(label4, 'this is a label!')
        createToolTip(label12, 'this is a label!')
        createToolTip(label13, 'this is a label!')
        createToolTip(bookNumChosen, 'this is a combobox!')
        createToolTip(bookNameChosen, 'this is a combobox!')
        createToolTip(checkBookNameChosen, 'this is a combobox!')
        createToolTip(bookNameChosen2, 'this is a combobox!')
        createToolTip(bookNameChosen3, 'this is a combobox!')
        createToolTip(bookNameChosen4, 'this is a combobox!')
        createToolTip(bookNameChosen5, 'this is a combobox!')
        createToolTip(peopleNameChosen, 'this is a combobox!')
        createToolTip(peopleNameChosen2, 'this is a combobox!')
        createToolTip(peopleNameChosen3, 'this is a combobox!')
        createToolTip(peopleNameChosen4, 'this is a combobox!')
        createToolTip(typeChosen, 'this is a combobox!')
        createToolTip(ent1, 'this is an entry!')
        createToolTip(ent2, 'this is an entry!')
        createToolTip(ent3, 'this is an entry!')
        createToolTip(ent4, 'this is an entry!')
        createToolTip(ent5, 'this is an entry!')
        createToolTip(ent6, 'this is an entry!')
        createToolTip(ent7, 'this is an entry!')
        createToolTip(ent9, 'this is an entry!')
        createToolTip(ent10, 'this is an entry!')
        createToolTip(ent11, 'this is an entry!')
        createToolTip(ent12, 'this is an entry!')
        createToolTip(ent13, 'this is an entry!')
        createToolTip(button1, 'this is a button!')
        createToolTip(button2, 'this is a button!')
        createToolTip(button3, 'this is a button!')
        createToolTip(button4, 'this is a button!')
        createToolTip(button5, 'this is a button!')
        createToolTip(button6, 'this is a button!')
        createToolTip(button7, 'this is a button!')
        createToolTip(button8, 'this is a button!')
        createToolTip(button9, 'this is a button!')
        createToolTip(button10, 'this is a button!')
        createToolTip(button11, 'this is a button!')
        createToolTip(button12, 'this is a button!')
        createToolTip(button13, 'this is a button!')
        createToolTip(button14, 'this is a button!')
        createToolTip(button15, 'this is a button!')
        createToolTip(button16, 'this is a button!')
        createToolTip(button17, 'this is a button!')
        createToolTip(button18, 'this is a button!')
        createToolTip(button19, 'this is a button!')
        createToolTip(check_P, 'this is a checkbutton!')
        createToolTip(check_B, 'this is a checkbutton!')
        createToolTip(check3, 'this is a checkbutton!')
        createToolTip(curRad_P0, 'this is a radiobutton!')
        createToolTip(curRad_P1, 'this is a radiobutton!')
        createToolTip(curRad_P2, 'this is a radiobutton!')
        createToolTip(curRad_P3, 'this is a radiobutton!')
        createToolTip(curRad_P4, 'this is a radiobutton!')
        createToolTip(curRad_B0, 'this is a radiobutton!')
        createToolTip(curRad_B1, 'this is a radiobutton!')
        createToolTip(curRad_B2, 'this is a radiobutton!')
        createToolTip(curRad_B3, 'this is a radiobutton!')
        createToolTip(curRad_B4, 'this is a radiobutton!')
        createToolTip(curRad_B5, 'this is a radiobutton!')
        createToolTip(text2, 'this is a scroll text!')
        createToolTip(text3, 'this is a scroll text!')
        createToolTip(spin, 'this is a spinbox!')
        createToolTip(spin1, 'this is a spinbox!')
        createToolTip(spin2, 'this is a spinbox!')
        createToolTip(spin3, 'this is a spinbox!')
        createToolTip(spin4, 'this is a spinbox!')
        createToolTip(spin5, 'this is a spinbox!')
        createToolTip(spin6, 'this is a spinbox!')
        root.mainloop()

    main()
