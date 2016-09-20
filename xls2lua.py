﻿#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Author: NormanYang

import xlrd
import os.path
import time
import os
import sys
import codecs

SCRIPT_HEAD = "-- This file is generated by program!\n\
-- Don't change it manaully.\n\
-- Author: chuxiang9007@163.com  NormanYang\n\
-- Source file: %s\n\
-- Created at: %s\n\
\n\
\n\
"

def make_table(filename):
	if not os.path.isfile(filename):
		sys.exit("%s is	not	a valid	filename" % filename)
	book_xlrd = xlrd.open_workbook(filename)

	excel = {}
	excel["filename"] = filename
	excel["data"] = {}
	excel["meta"] = {}
	for sheet in book_xlrd.sheets():
		sheet_name = sheet.name.replace(" ", "_")
		if not sheet_name.startswith("OUT_"):
			continue
		sheet_name = sheet_name[4:]
		print(sheet_name+" sheet")
		excel["data"][sheet_name] = {}
		excel["meta"][sheet_name] = {}

		# 必须大于3行 一行描述，一行键值，一行类型
		if sheet.nrows <= 3:
			return {}, -1, "sheet[" + sheet_name + "]" + " rows must > 3"

		# 解析标题
		title = {}
		col_idx = 0
		for col_idx in range(sheet.ncols):
			value = sheet.cell_value(1, col_idx)
			vtype = sheet.cell_type(1, col_idx)
			if vtype != 1:
				return {}, -1, "title columns[" + str(col_idx) + "] must be string"
			title[col_idx] = str(value).replace(" ", "_")
 
		excel["meta"][sheet_name]["title"] = title

		# 类型解析
		type_dict = {}
		col_idx = 0
		for col_idx in range(sheet.ncols):
			value = sheet.cell_value(2, col_idx)
			vtype = sheet.cell_type(2, col_idx)
			type_dict[col_idx] = str(value)
			if (type_dict[col_idx].lower() != "int" \
				and type_dict[col_idx].lower() != "float" \
				and type_dict[col_idx].lower() != "string" \
				and type_dict[col_idx].lower() != "boolean"\
				and type_dict[col_idx].lower() != "intarr"\
				and type_dict[col_idx].lower() != "floatarr"\
				and type_dict[col_idx].lower() != "stringarr"\
				and type_dict[col_idx].lower() != "booleanarr"):
				return {}, -1, "sheet[" + sheet_name + "]" + \
					" row[" + row_idx + "] column[" + col_idx + \
					"] type must be [i] or [string] or [boolean] or [intarr] or [stringarr] or [floatarr] or [booleanarr]"

		if type_dict[0].lower() != "int":
			return {}, -1,"sheet[" + sheet_name + "]" + " first column type must be [int]"

		excel["meta"][sheet_name]["type"] = type_dict

		row_idx = 3
		# 数据从第3行开始
		for row_idx in range(3, sheet.nrows):
			row = {}

			col_idx = 0
			for col_idx in range(sheet.ncols):
				value = sheet.cell_value(row_idx, col_idx)
				vtype = sheet.cell_type(row_idx, col_idx)
				# 本行有数据
				v = None
				if type_dict[col_idx].lower() == "int" and vtype == 2:
					v = int(value)
				elif type_dict[col_idx].lower() == "float" and vtype == 2:
					v = float(value)
				elif type_dict[col_idx].lower() == "string":
					v = format_str(value)
				elif type_dict[col_idx].lower() == "boolean" and vtype == 4:
					if value == 1:
						v = "true"
					else:
						v = "false"
				elif type_dict[col_idx].lower() == "intarr" and vtype == 1:
					v = str(value)
				elif type_dict[col_idx].lower() == "floatarr" and vtype == 1:
					v = str(value)
				elif type_dict[col_idx].lower() == "stringarr":
					v = format_str(value)
				elif type_dict[col_idx].lower() == "booleanarr" and vtype == 1:
					v = str(value)

				row[col_idx] = v

			excel["data"][sheet_name][row[0]] = row

	return excel, 0 , "ok"

def format_str(value):
	if type(value) == int or type(value) == float:
		value =  str(value)
	
	value = value.replace('\"','\\\"')
	value = value.replace('\'','\\\'')
	return value

def get_int(value):
	if value is None:
		return 0
	return value

def get_float(value):
	if value is None:
		return 0
	return value

def get_string(value):
	if value is None:
		return ""
	return value

def get_boolean(value):
	if value is None:
		return "false"
	return value

def get_array_int( value ):
	if value is None:
		return "{}"
	tmp_vec_str = value.split(';')
	res_str = "{"
	i = 0
	for val in tmp_vec_str:
		if val != None and val != "":
			if i != 0:
				res_str += ","
			res_str = res_str + val
			i+=1
	res_str += "}"
	return res_str

def get_array_float( value ):
	if value is None:
		return "{}"
	tmp_vec_str = value.split(';')
	res_str = "{"
	i = 0
	for val in tmp_vec_str:
		if val != None and val != "":
			if i != 0:
				res_str += ","
			res_str = res_str + val
			i+=1
	res_str += "}"
	return res_str

def get_array_string( value ):
	if value is None:
		return "{}"
	tmp_vec_str = value.split(';')
	res_str = "{"
	i = 0
	for val in tmp_vec_str:
		if val != None and val != "":
			if i != 0:
				res_str += ","
			res_str = res_str + "\"" + val + "\""
			i+=1
	res_str += "}"
	return res_str

def get_array_boolean( value ):
	if value is None:
		return "{}"
	tmp_vec_str = value.split(';')
	res_str = "{"
	i = 0
	for val in tmp_vec_str:
		if val != None and val != "":
			if i != 0:
				res_str += ","
			res_str = res_str + val.lower()
			i+=1
	res_str += "}"
	return res_str

def write_to_lua_script(excel, output_path):
	if not os.path.exists(output_path):
		os.mkdir(output_path)
	for (sheet_name, sheet) in excel["data"].items():
		outfp = codecs.open(output_path + "/" + sheet_name + ".lua", 'w', 'UTF-8')
		create_time = time.strftime("%a %b %d %H:%M:%S %Y", time.gmtime(time.time()))
		outfp.write(SCRIPT_HEAD % (excel["filename"], create_time)) 
		outfp.write("local data = {}\n")
		outfp.write("\n")
		
		title = excel["meta"][sheet_name]["title"]
		type_dict= excel["meta"][sheet_name]["type"]
		
		for (row_idx, row) in sheet.items():
			outfp.write("data[" + str(row[0]) + "] = {")
			field_index = 0
			for (col_idx, field)in row.items():
				if field_index > 0:
						outfp.write(", ")
				field_index += 1
				if type_dict[col_idx] == "int":
					tmp_str = get_int(row[col_idx])
					outfp.write(" " + str(title[col_idx]) + " = " + str(tmp_str))
				elif type_dict[col_idx] == "float":
					tmp_str = get_float(row[col_idx])
					outfp.write(" " + str(title[col_idx]) + " = " + str(tmp_str))
				elif type_dict[col_idx] == "string":
					tmp_str = get_string(row[col_idx])
					outfp.write(" " + str(title[col_idx]) + " = \"" + str(tmp_str) + "\"")
				elif type_dict[col_idx] == "boolean":
					tmp_str = get_boolean(row[col_idx])
					outfp.write(" " + str(title[col_idx]) + " = " + str(tmp_str))
				elif type_dict[col_idx] == "intArr":
					tmp_str = get_array_int(row[col_idx])
					outfp.write(" " + str(title[col_idx]) + " = " + str(tmp_str))
				elif type_dict[col_idx] == "floatArr":
					tmp_str = get_array_float(row[col_idx])
					outfp.write(" " + str(title[col_idx]) + " = " + str(tmp_str))
				elif type_dict[col_idx] == "stringArr":
					tmp_str = get_array_string(row[col_idx])
					outfp.write(" " + str(title[col_idx]) + " = " + str(tmp_str))
				elif type_dict[col_idx] == "booleanArr":
					tmp_str = get_array_boolean(row[col_idx])
					outfp.write(" " + str(title[col_idx]) + " = " + str(tmp_str))
				else:
					outfp.close()
					sys.exit("error: there is some wrong in type.")

			outfp.write("}\n")

		outfp.write("\nreturn data\n")
		outfp.close()

def handler_file(excel_name, output_path):
	data, ret, errstr = make_table(excel_name)
	if ret != 0:
		print(excel_name)
		print("error: " + errstr)
	else:
		print(excel_name)
		print("res:")
		# print(data)
		print("success!!!")
	write_to_lua_script(data, output_path)


def handler_path(excel_path, output_path):
	from platform import python_version
	print('Python', python_version())

	if (os.path.exists(output_path)==False):
		os.makedirs(output_path)

	for parent,dirnames,filenames in os.walk(excel_path):
		for filename in filenames:                         
			if (parent == excel_path):
				handler_file(os.path.join(parent,filename), output_path)

if __name__=="__main__":
	reload(sys)
	sys.setdefaultencoding('utf-8')
	handler_path("./excelData/", "./Config/")