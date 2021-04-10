import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import Backend
import Settings

class SearchFrame(tk.Frame):
    def __init__(self, root, settingsCallback=None, recCallback=None):
        tk.Frame.__init__(self, root)
        self.root = root

        self._settings = settingsCallback
        self._displayRec = recCallback
        
        self._draw()

    def searchAnimeTitle(self, event=None):
        pauseMenu = tk.Toplevel(self.root)
        pauseMenu.title("")
        width, height = 200, 100
        x = int(self.root.winfo_screenwidth()/2 - width/2)
        y = int(self.root.winfo_screenheight()/2 - height/2)
        pauseMenu.geometry('%dx%d+%d+%d' % (width, height, x, y))
        pauseMenu.resizable(False, False)
        pauseMenu.attributes('-topmost', True)
        label = tk.Label(pauseMenu, text="\nSearching anime...")
        label.pack()
        label.wait_visibility()
        pauseMenu.update()

        for item in self.titleTree.get_children():
            self.titleTree.delete(item)

        query = self.searchBox.get('1.0', 'end').rstrip()
        try:
            results = Backend.searchTitles(query, "anime")

            for x in range(len(results)):
                self.insertIntoTree(x, results[x], "anime")

            self.searchBox.delete('1.0', 'end')

            pauseMenu.destroy()

        except:
            tk.messagebox.showinfo(title='No results.', message="There were no search results.", parent=pauseMenu)
            pauseMenu.destroy()
            

    def searchMangaTitle(self):
        pauseMenu = tk.Toplevel(self.root)
        pauseMenu.title("")
        width, height = 200, 100
        x = int(self.root.winfo_screenwidth()/2 - width/2)
        y = int(self.root.winfo_screenheight()/2 - height/2)
        pauseMenu.geometry('%dx%d+%d+%d' % (width, height, x, y))
        pauseMenu.resizable(False, False)
        pauseMenu.attributes('-topmost', True)
        label = tk.Label(pauseMenu, text="\nSearching manga...")
        label.pack()
        label.wait_visibility()
        pauseMenu.update()

        for item in self.titleTree.get_children():
            self.titleTree.delete(item)

        query = self.searchBox.get('1.0', 'end').rstrip()
        try:
            results = Backend.searchTitles(query, "manga")

            for x in range(len(results)):
                self.insertIntoTree(x, results[x], "manga")

            self.searchBox.delete('1.0', 'end')

            pauseMenu.destroy()

        except:
            tk.messagebox.showinfo(title='No results.', message="There were no search results.", parent=pauseMenu)
            pauseMenu.destroy()

    def getRecommendations(self):
        pauseMenu = tk.Toplevel(self.root)
        pauseMenu.title("")
        width, height = 200, 100
        x = int(self.root.winfo_screenwidth()/2 - width/2)
        y = int(self.root.winfo_screenheight()/2 - height/2)
        pauseMenu.geometry('%dx%d+%d+%d' % (width, height, x, y))
        pauseMenu.resizable(False, False)
        pauseMenu.attributes('-topmost', True)
        label = tk.Label(pauseMenu, text="\nGenerating recommendations...\n(takes ~15 seconds)")
        label.pack()
        label.wait_visibility()
        pauseMenu.update()

        if self.titleTree.focus() != '':
            item = self.titleTree.item(self.titleTree.focus())
        
        else:
            item = self.titleTree.item('0')

        titleID = item['values'][0]
        titleName = item['values'][1]
        medium = item['tags'][0]

        userList = Backend.getSimilarUsers(titleID, medium)

        if len(userList) == 0:
            tk.messagebox.showinfo(title='No reference data.', message=str(titleName) + " has no user reviews to reference.", parent=pauseMenu)
            pauseMenu.destroy()
            return

        recommendedList = Backend.getRecommendedList(userList, self._settings, medium)

        if len(recommendedList) == 0:
            tk.messagebox.showinfo(title='No results.', message="There were no results with the current search settings.", parent=pauseMenu)
            pauseMenu.destroy()
            return

        if titleName in recommendedList:
            recommendedList.remove(titleName)

        self._displayRec(recommendedList, titleName, self._settings)

        pauseMenu.destroy()

    def insertIntoTree(self, id, entry: str, medium: str):
        self.titleTree.insert('', id, id, values=entry, tags=medium)    

    def _draw(self):
        self.searchBox = tk.Text(master=self, height=1, width=50, wrap='none')
        self.searchBox.config(wrap='none')
        self.searchBox.pack(expand=False, padx=10, pady=10)
        self.searchBox.bind('<Return>', self.searchAnimeTitle)

        buttonsRow = tk.Frame(self, height=1)
        buttonsRow.pack(expand=False, padx=10)

        animeButton = tk.Button(buttonsRow, text="Anime search", width=20, height=1)
        animeButton.configure(command=self.searchAnimeTitle)
        animeButton.pack(side=tk.LEFT, padx=5, pady=0, expand=False)

        mangaButton = tk.Button(buttonsRow, text="Manga search", width=20, height=1)
        mangaButton.configure(command=self.searchMangaTitle)
        mangaButton.pack(side=tk.LEFT,padx=5, pady=0, expand=False)

        searchFrame = tk.Frame(master=self, width=10)
        searchFrame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)
        self.titleTree = ttk.Treeview(searchFrame)
        self.titleTree['columns'] = ("ID", "Title")
        self.titleTree.column("#0", stretch=tk.NO, minwidth=0, width=0)
        self.titleTree.column("ID", stretch=tk.NO, minwidth=0, width=0)
        self.titleTree.column("Title", width=100)

        self.titleTree.heading("#0", text="", anchor=tk.W)
        self.titleTree.heading("ID", text="ID:", anchor=tk.W)
        self.titleTree.heading("Title", text="Search results (select title):", anchor=tk.W)
        self.titleTree.pack(fill=tk.BOTH, expand=True)


        recButton = tk.Button(self, text="Get recommendations", width=20, height=1)
        recButton.configure(command=self.getRecommendations)
        recButton.pack(side=tk.LEFT, padx=5, pady=0, expand=True)


class ResultFrame(tk.Frame):
    def __init__(self, root, settingsCallback=None):
        tk.Frame.__init__(self, root)
        self.root = root

        self._settingsCallback = settingsCallback
        
        self._draw()

    def displayRecommendations(self, recList, titleName, settings: Settings.userSettings):
        for item in self.titleTree.get_children():
            self.titleTree.delete(item)

        for x in range(len(recList)):
            self.titleTree.insert('', x, x, text=str(x+1)+'. '+recList[x])

        self.label['text'] = "Users that liked " + str(titleName) + " tend to like these titles from " + str(settings.minYear) + " to " + str(settings.maxYear) + ":"

    def _draw(self):
        resultsFrame = tk.Frame(master=self, width=250)
        resultsFrame.pack(side=tk.LEFT, padx=5)
        self.label = tk.Label(resultsFrame, text='No title selected.\n', wraplength=275)
        self.label.pack()
        self.titleTree = ttk.Treeview(resultsFrame)
        self.titleTree.column("#0", width=340)
        self.titleTree.heading("#0", text="Recommendations:", anchor=tk.W)
        self.titleTree.pack(side=tk.TOP, expand=False, padx=5, pady=5)

class MainApp(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        self.settings = Settings.userSettings()

        self._draw()

    def focusNext(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def saveSettings(self, event=None):
        try:
            self.settings.minYear = int(self.minYearBox.get('1.0', 'end').rstrip())
            self.settings.maxYear = int(self.maxYearBox.get('1.0', 'end').rstrip())

            if self.settings.maxYear < self.settings.minYear:
                temp = self.settings.maxYear
                self.settings.maxYear = self.settings.minYear
                self.settings.minYear = temp

            username = self.usernameBox.get('1.0', 'end').rstrip() 

            if username != self.settings.MALUsername:
                pauseMenu = tk.Toplevel(self.root)
                pauseMenu.title("")
                width, height = 200, 100
                x = int(self.root.winfo_screenwidth()/2 - width/2)
                y = int(self.root.winfo_screenheight()/2 - height/2)
                pauseMenu.geometry('%dx%d+%d+%d' % (width, height, x, y))
                pauseMenu.resizable(False, False)
                pauseMenu.attributes('-topmost', True)
                label = tk.Label(pauseMenu, text="\nRetrieving user list...\n(big lists take longer to retrieve)")
                label.pack()
                label.wait_visibility()
                pauseMenu.update()

                self.settings.MALUsername = username
                Backend.filterUserList(self.settings)

                pauseMenu.destroy()

            self.settingsWindow.destroy()

        except ValueError:
            tk.messagebox.showinfo(title='Invaild Date', message='Please enter a valid date range.', parent=self.settingsWindow)
        except:
            pauseMenu.destroy()
            tk.messagebox.showinfo(title='Username Error', message='Failed to retrieve user list.', parent=self.settingsWindow)

    def openSettings(self):
        self.settingsWindow = tk.Toplevel(self.root)
        self.settingsWindow.title("User Settings")
        width, height = 400, 100
        x = int(self.root.winfo_screenwidth()/2 - width/2)
        y = int(self.root.winfo_screenheight()/2 - height/2)
        self.settingsWindow.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.settingsWindow.resizable(False, False)
        self.settingsWindow.attributes('-topmost', True)

        # The first frame which lets the user change the date range of recommendations
        row1 = tk.Frame(self.settingsWindow, height=50)
        row1.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=10, pady=5)
        tk.Label(row1, text='Date range of recommendations:  ').pack(side=tk.LEFT)

        self.minYearBox = tk.Text(row1, height=1, width=10, wrap='none')
        self.minYearBox.pack(side=tk.LEFT, expand=True)
        self.minYearBox.bind("<Tab>", self.focusNext)
        self.minYearBox.bind("<Return>", self.saveSettings)

        tk.Label(row1, text='to').pack(side=tk.LEFT)

        self.maxYearBox = tk.Text(row1, height=1, width=10, wrap='none')
        self.maxYearBox.pack(side=tk.LEFT, expand=True)
        self.maxYearBox.bind("<Tab>", self.focusNext)
        self.maxYearBox.bind("<Return>", self.saveSettings)

        self.minYearBox.insert(1.0, self.settings.minYear)
        self.maxYearBox.insert(1.0, self.settings.maxYear)

        # The second frame which lets the user input a MyAnimeList username to filter results
        row2 = tk.Frame(self.settingsWindow, height=50)
        row2.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=10)
        tk.Label(row2, text='MyAnimeList username: ').pack(side=tk.LEFT)

        self.usernameBox = tk.Text(row2, height=1, wrap='none')
        self.usernameBox.pack(side=tk.LEFT, expand=True)
        self.usernameBox.bind("<Tab>", self.focusNext)
        self.usernameBox.bind("<Return>", self.saveSettings)

        self.usernameBox.insert(1.0, self.settings.MALUsername)

        saveButton = tk.Button(self.settingsWindow, text="Save", width=20, height=10)
        saveButton.configure(command=self.saveSettings)
        saveButton.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5, expand=False)

    def close(self):
        self.root.destroy()

    def _draw(self):
        menuBar = tk.Menu(self.root)
        self.root['menu'] = menuBar
        menuFile = tk.Menu(menuBar)
        menuBar.add_cascade(menu=menuFile, label='File')
        menuFile.add_command(label='Settings', command=self.openSettings)
        menuFile.add_command(label='Close', command=self.close)

        self.resultFrame = ResultFrame(self.root)
        self.resultFrame.pack(side=tk.RIGHT, expand=False)

        self.searchFrame = SearchFrame(self.root, self.settings, self.resultFrame.displayRecommendations)
        self.searchFrame.pack(side=tk.LEFT, expand=True)

if __name__ == "__main__":
    main = tk.Tk()
    main.title("Jikan Recommender")
    mainWidth, mainHeight = 720, 380
    mainX = int(main.winfo_screenwidth()/2 - mainWidth/2)
    mainY = int(main.winfo_screenheight()/2 - mainHeight/2)
    main.geometry('%dx%d+%d+%d' % (mainWidth, mainHeight, mainX, mainY))
    main.option_add('*tearOff', False)
    MainApp(main)
    main.resizable(False, False)
    main.mainloop()
