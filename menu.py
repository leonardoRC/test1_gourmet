menu = ["1 - create database.","2 - Import data.","3 - query all sequences.","4 exit ",]
while True:
    for entry in menu:
      print (entry)

    selection=input("Please Select:")
    if selection =='1':
      print ("add")
    elif selection == '2':
      print ("delete")
    elif selection == '3':
      print ("find")
    elif selection == '4':
      break
    else:
      print ("Unknown Option Selected!")