import turtle
import math
import time

# إعدادات الشاشة
turtle.bgcolor("black")
turtle.speed(0)
turtle.colormode(255)
turtle.tracer(0)

pen = turtle.Turtle()
pen.hideturtle()
pen.width(2)
pen_color = (120, 0, 0)  # لون القلب

rays = 120
step = 360 / rays
scale = 10  

# دالة لرسم نقاط القلب
def heart_point(angle):
    t = math.radians(angle)
    x = (16 * math.sin(t)**3) * scale
    y = (13*math.cos(t) - 5*math.cos(2*t) -
         2*math.cos(3*t) - math.cos(4*t)) * scale
    return x, y

# رسم القلب بأشعة
for i in range(rays):
    angle = i * step
    x_end, y_end = heart_point(angle)

    pen.pencolor(pen_color)
    pen.penup()
    pen.goto(0, 0)
    pen.pendown()

    steps = 60
    for s in range(steps + 1):
        x = (x_end * s) / steps
        y = (y_end * s) / steps
        pen.goto(x, y)
        turtle.update()
        time.sleep(0.0005)

# كتابة الاسم في منتصف القلب بخط روماني مع تأثير وميض
text_pen = turtle.Turtle()
text_pen.hideturtle()
text_pen.penup()
text_pen.goto(0, -20)

glow_colors = [
    (255, 255, 255),  # أبيض ساطع
    (255, 200, 200),  # وردي فاتح
    (255, 150, 150),  # وردي متوسط
    (255, 100, 100),  # وردي غامق
    (255, 150, 150),
    (255, 200, 200)
]


while True:
    for color in glow_colors:
        text_pen.clear()
        text_pen.color(color)
        text_pen.write("Eren", align="center", font=("Times New Roman", 36, "bold"))
        turtle.update()
        time.sleep(0.15)
