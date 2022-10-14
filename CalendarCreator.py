import pygame

from ImageManipulation import Image, Canvas
from MyAnimeListAPI import GetAnimeList, ImageDownloader


class CalendarEvent:
    def __init__(self, name, image : Image):
        self.name = name
        self.image = image
    
    def getName(self):
        return self.name
    def getImage(self) -> Image:
        return self.image

class Calendar:
    monthsList = [
    "january",
    "febuary",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december"
    ]
    monthDaysMap = {
    "january"   : 31,
    "febuary"   : 28,
    "march"     : 31,
    "april"     : 30,
    "may"       : 31,
    "june"      : 30,
    "july"      : 31,
    "august"    : 31,
    "september" : 30,
    "october"   : 31,
    "november"  : 30,
    "december"  : 31
    }

    def __init__(self, month, year):
        self.year = year
        
        if isinstance(month, int):
            if month > 0 and month <= 12:
                self.monthInt = month
                self.monthWord = Calendar.monthsList[self.monthInt-1]
            else:
                exit()
        elif isinstance(month, str):
            if month.lower() in Calendar.monthsList:
                self.monthWord = month.lower()
                self.monthInt = Calendar.monthsList.index(self.monthWord) + 1
            else:
                exit()

        self.days = Calendar.monthDaysMap[self.monthWord]
        if self.monthInt == 2:
            self.days += self.checkLeapYear(self.year)

        self.calendarList = [[] for _ in range(self.days)]

    def printData(self):
        print(f"{self.monthWord} {self.year}")
        print(f"Month (int): {self.monthInt}")
        print(f"Days in {self.monthWord} {self.year}: {self.days} \n")

    def addEvent(self, event : CalendarEvent, day : int):
        self.calendarList[day-1].append(event)

    def getMonthInt(self):
        return self.monthInt
    def getMonthStr(self):
        return self.monthWord
    def getYear(self):
        return self.year

    def generateImage(self):
        # 7 * 5
        boxesAcross = 7
        boxesTall = 5
        boxWidth = 200
        boxHeight = 150
        lineThickness = 2

        width = boxWidth * boxesAcross + (boxesAcross + 1) * lineThickness
        height = boxHeight * boxesTall + (boxesTall + 1) * lineThickness

        canvas = Canvas(width, height, [255, 255, 255])

        #print(f"Canvas Size - x: {width}, y: {height}")
        addedLines = 0
        for i in range(0, boxesAcross):
            #print(f"Adding Vertical Line at {i*boxWidth}, {i*boxWidth+1}")
            canvas.addLine([i*boxWidth + addedLines * lineThickness, i*boxWidth + addedLines * lineThickness + 1], [0,0,0], "vertical")
            addedLines += 1
        canvas.addLine([-1, -2], [0,0,0], "vertical")

        addedLines = 0
        for i in range(0, boxesTall):
            #print(f"Adding Horizontal Line at {i*boxWidth}")
            canvas.addLine([i*boxHeight + addedLines * lineThickness, i*boxHeight + addedLines * lineThickness + 1], [0,0,0], "horizontal")
            addedLines += 1
        canvas.addLine([-1, -2], [0,0,0], "horizontal")

        for i, day in enumerate(self.calendarList):
            added = 0
            print(f"{i + 1} : {day}")
            for event in day:
                if added < 2:
                    imageSize = [100, 150]
                    xPos = int(lineThickness + (((i%boxesAcross) * (boxWidth + lineThickness)) + imageSize[0] * added))
                    yPos = int(lineThickness + ((i//boxesAcross) * (boxHeight + lineThickness)))
                    position = [xPos, yPos]

                    #print(position)
                
                    canvas.blitImage(event.getImage(), position, size = imageSize)
                    added += 1


        canvas.update()
        return canvas

    @staticmethod
    def checkLeapYear(year):
        if not year % 100:
            return not year % 400
        else:
            return not year % 4


# Gets full anime list
animeList = GetAnimeList.GetDetailed("mattyboyh2003")
# Cuts the list down to only completed anime
animeList = [anime for anime in animeList if anime["list_status"]["status"] == "completed"]

calendar = Calendar("july", 2022)
calendar.printData()

hasStartDate = [anime for anime in animeList if "start_date" in list(anime["list_status"].keys())]
hasFinishDate = [anime for anime in animeList if "finish_date" in list(anime["list_status"].keys())]

startedThisMonth = [anime for anime in hasStartDate if int(anime["list_status"]["start_date"].split("-")[1]) == calendar.getMonthInt()]
finishedThisMonth = [anime for anime in hasFinishDate if int(anime["list_status"]["finish_date"].split("-")[1]) == calendar.getMonthInt()]

sortLambda = lambda a : ((int(a["list_status"]["start_date"].split("-")[0])-2000) * 367) + (int(a["list_status"]["start_date"].split("-")[1]) * 32) + int(a["list_status"]["start_date"].split("-")[2])

startedThisMonth.sort(key = sortLambda)
finishedThisMonth.sort(key = sortLambda)

#print(f"Animes started in {calendar.getMonthStr().capitalize()} {calendar.getYear()}:")
for anime in startedThisMonth:
    print(f"    {anime['node']['title']} : {anime['list_status']['start_date']}")
    calendar.addEvent(CalendarEvent(f"Started | {anime['node']['title']}", Image(file = ImageDownloader.DownloadImage(anime['node']['id'], "anime"))), int(anime['list_status']['start_date'].split("-")[2]))

#print(f"Animes finished in {calendar.getMonthStr()} {calendar.getYear()}:")
#for anime in finishedThisMonth:
    #print(f"    {anime['node']['title']} : {anime['list_status']['start_date']}")
    #calendar.addEvent(CalendarEvent(f"Finished | {anime['node']['title']}", Image(file = ImageDownloader.DownloadImage(anime['node']['id'], "anime"))), int(anime['list_status']['start_date'].split("-")[1]))

fullCalendar = calendar.generateImage()

fullCalendar.saveImage("Test.jpg", "jpg")

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
    clock.tick(30)
