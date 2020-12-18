import xlwt

def prepare_report(brand_name,stores_dict_list):
    if not stores_dict_list:
        return None
    
    wb = xlwt.Workbook()
    ws = wb.add_sheet(brand_name)
    
    widths = [40,50,15,6,12,12,14,14]
    for col_number , w in enumerate(widths):
        ws.col(col_number).width = 256*w

    #writing column name
    ws.write(0, 0, 'Store Name')
    ws.write(0, 1, 'Street Address')
    ws.write(0, 2, 'City')
    ws.write(0, 3, 'State')
    ws.write(0, 4, 'Zip Code')
    ws.write(0, 6, 'Longitude')
    ws.write(0, 5, 'Phone Number')
    ws.write(0, 7, 'Latitude')

    #writing data to the columns.
    row_index = 1
       
    for store in stores_dict_list:
        ws.write(row_index, 0, store.get('storeName'))
        ws.write(row_index,1,store.get('address'))
        ws.write(row_index,2,store.get('city'))
        ws.write(row_index,3,store.get('state'))
        ws.write(row_index,4,store.get('zip'))
        ws.write(row_index,5,store.get('phone'))
        ws.write(row_index,6,store.get('longitude'))
        ws.write(row_index,7,store.get('latitude'))
        row_index = row_index + 1 
            
    # saving the workbook
    #wb.save('Smart and Final.xls')
    return wb

if __name__ == "__main__":
    prepare_report('smart and final',{})