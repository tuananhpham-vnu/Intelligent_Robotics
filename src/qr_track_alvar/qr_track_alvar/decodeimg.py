#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw, ImageFont

	
def decodeimg(img, flag):	
	#print("decode init")
	#调用decode()函数,返回的信息包含尺寸rect,数据data
	codes = decode(img)
	#print(len(codes))
	if len(codes) == 0:
		img = cv2ImgAddText(img, "没有识别到!", 40, 40)
		#cv2.putText(img, 'No Track!', (40, 4S0), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,255), 2)
		if flag == 0:
			cv2.namedWindow("qr_track_alvar",0);
			cv2.resizeWindow("qr_track_alvar", 640, 480);#640, 480
			cv2.imshow('qr_track_alvar', img)
		else:			
			cv2.namedWindow("本地识别",0);
			cv2.resizeWindow("本地识别", 640, 480);
			cv2.imshow('本地识别', img)
		cv2.waitKey(1)
		return ""
	#打印出二维码信息
	if len(codes) > 0:
		for code in codes:
			result = code.data.decode("utf-8")
			#print(result)
			pts = np.array([code.polygon], np.int32)
			pts = pts.reshape((-1, 1, 2))
			cv2.polylines(img, [pts], True, (255,255,255), 5)
			pts2 = code.rect
			img = cv2ImgAddText(img, result, pts2[0], pts2[1])
			#cv2.putText(img, result, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,255), 2)
			if flag == 0:
				cv2.namedWindow("qr_track_alvar",0);
				cv2.resizeWindow("qr_track_alvar", 640, 480);
				cv2.imshow('qr_track_alvar', img)
			else:			
				cv2.namedWindow("本地识别",0);
				cv2.resizeWindow("本地识别", 640, 480);
				cv2.imshow('本地识别', img)
			cv2.waitKey(1)
			return result
			


# 解决cv2.putText绘制中文乱码
def cv2ImgAddText(img2, text, left, top, textColor=(255, 0, 0), textSize=12):
	if isinstance(img2, np.ndarray):  # 判断是否OpenCV图片类型
		img2 = Image.fromarray(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
	# 创建一个可以在给定图像上绘图的对象
	draw = ImageDraw.Draw(img2)
	# 字体的格式
	fontStyle = ImageFont.truetype('/usr/NotoSansCJK-Regular.otf', textSize, encoding="utf-8")
	# 绘制文本
	draw.text((left, top), text, textColor, font=fontStyle)
	# 转换回OpenCV格式
	return cv2.cvtColor(np.asarray(img2), cv2.COLOR_RGB2BGR)
