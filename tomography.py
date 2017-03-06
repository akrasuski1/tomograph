from PIL import Image, ImageDraw
import math

def generate_beams(n_emitters, l_spread, w, alpha):
    p1=[]
    p2=[]
    div=1.03 # Avoid edges
    for j in range(n_emitters):
        d=l_spread*w*(-0.5+j/(n_emitters-1.0))
        x=d
        y=math.sqrt(w*w/4.0-d*d)
        x, y = x/div, y/div
        x, y = (x*math.cos(alpha)-y*math.sin(alpha),
                x*math.sin(alpha)+y*math.cos(alpha))
        x+=w/2.0
        y+=w/2.0
        x=int(math.floor(x))
        y=int(math.floor(y))
        p1.append((x, y))
        p2.append((w-1-x, w-1-y))
    return zip(p1, p2[::-1])

def update_sinogram(im, sino, q1, q2, i, j):
    # Not using Bresenham! It's wrong!
    w=im.size[0]
    sm=0
    d=int(((q2[0]-q1[0])**2+(q2[1]-q1[1])**2)**0.5)
    data=im.getdata()
    for k in range(d):
        x=int(q1[0]+(q2[0]-q1[0])*float(k)/d)
        y=int(q1[1]+(q2[1]-q1[1])*float(k)/d)
        sm+=data[y*w+x]
    pix=sm/w # Normalization - max would be 255*w, but we divide by w.
    sino.putpixel((i, j), pix)

# Using parallel tomograph.
def make_sinogram_from_image(img_name, simg_dir, scan_dir, 
        l_spread=0.5, # Ratio of detector spread to circle diameter
        n_samples=100,
        n_emitters=30):
    im=Image.open(img_name).convert("L")
    w, h = im.size
    assert w==h

    sino=Image.new("L", (n_samples, n_emitters))
    for i in range(n_samples):
        print i,"/",n_samples
        sim=im.copy().convert("RGB")
        alpha=math.pi/n_samples*i
        beams=generate_beams(n_emitters, l_spread, w, alpha)
        for j, (q1, q2) in enumerate(beams):
            draw=ImageDraw.Draw(sim)
            x1, y1=q1[0], q1[1]
            x2, y2=q2[0], q2[1]
            draw.ellipse((x1-2, y1-2, x1+2, y1+2), fill=(255, 0, 0))
            draw.ellipse((x2-2, y2-2, x2+2, y2+2), fill=(255, 0, 0))
            draw.line((x1, y1, x2, y2), fill=(128, 0, 0))

            update_sinogram(im, sino, q1, q2, i, j)
        sim.save(scan_dir+"/"+str(i)+".png")
        sino.save(sinogram_dir+"/"+str(i)+".png")

    sino.save(sinogram_dir+"/final_sinogram.png")

def det(beam, c):
    a=beam[0]
    b=beam[1]
    return a[0]*b[1] + b[0]*c[1] + c[0]*a[1] - a[0]*c[1] - b[0]*a[1] - c[0]*b[1]

def dist_point_line(beam, c):
    a=beam[0]
    b=beam[1]
    x1=a[0]
    y1=a[1]
    x2=b[0]
    y2=b[1]
    x0=c[0]
    y0=c[1]
    return abs( (y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / ( (y2-y1)**2 + (x2-x1)**2 )**0.5

def make_image_from_sinogram(sin_file, reco_dir, l_spread=0.5, use_filter=False):
    sino=Image.open(sin_file)
    n_samples, n_emitters = sino.size
    w=512
    data=[0]*w*w
    sdata=sino.getdata()
    for i in range(n_samples):
        print i,"/",n_samples
        alpha=math.pi/n_samples*i
        beams=generate_beams(n_emitters, l_spread, w, alpha)
        view=[]
        for j, (q1, q2) in enumerate(beams):
            d=((q2[0]-q1[0])**2+(q2[1]-q1[1])**2)**0.5
            avg=sdata[i+j*n_samples]/d
            view.append(avg)
        if use_filter:
            new_view=[0]*len(view)
            # Filter kernel:
            # h[0]=1
            # h[k]=0 for even k
            # h[k]=-4/pi/pi/k/k for odd k
            for j in range(len(view)):
                for d in range(len(view)):
                    k=d-j
                    if k<0:
                        k=-k
                    if k==0:
                        new_view[j]+=view[d]
                    elif k%2==1:
                        new_view[j]-=4/math.pi**2/k**2*view[d]
            view=new_view
        for x in range(w):
            nextline=0
            for y in range(w):
                while nextline!=len(beams) and det(beams[nextline], (x, y))>0:
                    nextline+=1
                if nextline==0:
                    data[x+y*w]+=view[nextline]
                elif nextline==len(beams):
                    data[x+y*w]+=view[-1]
                else:
                    d1=dist_point_line(beams[nextline-1], (x,y))
                    d2=dist_point_line(beams[nextline], (x,y))
                    if d1<d2:
                        data[x+y*w]+=view[nextline-1]
                    else:
                        data[x+y*w]+=view[nextline]


        reco=Image.new("L", (w, w))
        mx=max(data)
        mn=min(data)
        if mx<1:
            mx=1
        if mn==mx:
            mx+=1
        norm=[int(255*(x-mn)/(mx-mn)) for x in data]
        reco.putdata(norm)
        reco.save(reco_dir+"/"+str(i)+".png")
    reco.save(reco_dir+"/final_reconstruction.png")

if __name__=="__main__":
    import sys
    input_image=sys.argv[1]
    sinogram_dir=sys.argv[2]
    scan_dir=sys.argv[3]
    reconstruction_dir=sys.argv[4]
    l_spread=0.9
    n_samples=180
    n_emitters=100
    use_filter=True
    make_sinogram_from_image(input_image, sinogram_dir, scan_dir, l_spread, n_samples, n_emitters)
    make_image_from_sinogram(sinogram_dir+"/final_sinogram.png", reconstruction_dir, l_spread, use_filter)
