import socket , re
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

import random, sys, getopt
import collections
#import gobject
import os
import queue
from queue import Queue, Empty
import threading
import _thread
import datetime
import select



def get_local_ip():
        def udp_listening_server():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('<broadcast>', 8888))
            s.setblocking(0)
            while True:
                result = select.select([s],[],[])
                msg, address = result[0][0].recvfrom(1024)
                msg = str(msg, 'UTF-8')
                if msg == 'What is my LAN IP address?':
                    break
            queue.put(address)

        queue = Queue()
        thread = threading.Thread(target=udp_listening_server)
        thread.queue = queue
        thread.start()
        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        waiting = True
        while waiting:
            s2.sendto(bytes('What is my LAN IP address?', 'UTF-8'), ('<broadcast>', 8888))
            try:
                address = queue.get(False)
            except Empty:
                pass
            else:
                waiting = False
        print (address[0])
        return address[0]
# function to find elem in l
def find(l, elem):
        # for all elements in l, row is the line, i is l[row]
    ret_y=-1
    #print l,elem
    for row, i in enumerate(l):
        try:
            #print row,i,elem
            column = i.index(elem) # get the index of elem in i
            return row,column
        except ValueError:
            ret_y=0
            #print "value error"
            #m=re.search(i[0],elem,re.IGNORECASE) # we try to see if this is a string that contains elem
            #if m:
            #       return row, 1 # if yes, we take the column to be 1,
            #else:
            continue
    return -1,ret_y # if we're here, it means the list l is empty or we did not find elem there

def get_args(argv):
        try:
              opts, args = getopt.getopt(argv,"hp:q:o:g:",["port=","graphs=","queries=","output="])
        except getopt.GetoptError:
              print('server_qt_simple.py [-h] -p port_number [-g graphs |-q number_of_queries |-o output_file_name] ')
              sys.exit(2)
        outfile=''
        queries=0
        queries_list=[]
        queries_set=''
        graphs=-1
        if len(opts)<1:
              print('server_qt_simple.py [-h] -p port_number [-g number_of_graphs -q list_of_queries -o output_file_name ]')
              sys.exit(2)
        for opt, arg in opts:
              if opt == '-h':
                      print('server_qt_simple.py -p port_number [-g number_of_graphs | -q list_of_queries |-o output_file_name]')
                      print('-p gives the port number on which to listen, must be the same in your parfile')
                      print('-q the list of queries you want to graph, otherwise all of them. Tt can also be something like this')
                      print('   "q1,q2,q4.*" ')
                      print('-o specifies that you want the data to be saved to a file for later processing')
                      print('-g number of graphs, it defaults to 1')
                      sys.exit()
              elif opt in ("-p", "--port"):
                 port = arg
              elif opt in ("-q", "--queries"):
                 queries_set = arg
              elif opt in ("-g", "--graphs"):
                 graphs = int(arg)
              elif opt in ("-o", "--output"):
                  outfile=arg
        if graphs==-1 and outfile=='':
              print('Please either specify -o, or -g or both')
              print('server_qt_simple.py [-h] -p port_number [-q list_of_queries -o output_file_name -g number_of_graphs ]')
              sys.exit(2)
        for i in range(graphs):
                queries_list.append([])
        if queries_set!='':
                grp_of_queries=queries_set.split(',')
                i=0
                queries=len(grp_of_queries)
                for grps in grp_of_queries:
                        queries_list[i].append(grps)
                        i+=1
                        if i>=graphs:
                                i=0
        return int(port), int(queries), outfile,queries_list,graphs

class handler(threading.Thread):
        def __init__(self, clientsock_p, addr_p, timer_init_p, dqueue_query_p, dqueuedata_p, outfile_p,queries_list,got_queries_p, graphs_p, lock):
                self.timer=timer_init_p
                self.timer_init1=timer_init_p
                self.outfile=outfile_p
                self.dqueuedata=dqueuedata_p
                self.dqueue_query=dqueue_query_p
                self.clientsock=clientsock_p
                self.addr=addr_p
                self.graphs=graphs_p
                self.clientsock.settimeout(1)
                #self._stop = threading.Event()
                self.queries_list=queries_list
                self.got_queries=got_queries_p
                self.lock=lock;
                threading.Thread.__init__(self)
        def stopit(self):
                #print 'I was asked to stop',threading.current_thread()
                self.clientsock.close()
                #self._stop.set()

        #def stopped(self):
                #print 'checking if I was asked to stop',threading.current_thread()
         #       return self._stop.isSet()

        def run(self):
                old_data=''
                oldquery=''
                BUFSIZ=1250
                listen=1
                #print "listening ",self.timer_init1,self.timer
                query_name=''
                # message field description
                # f1: trial nbr
                # f2: query name
                # f3: process pid
                # f4: execution timestamp
                # f5: execution time
                # f6: row count
                # f7: line in bind file
                d=datetime.datetime.now()
                while listen:
                        try:
                                data = old_data+str(self.clientsock.recv(BUFSIZ),encoding='UTF-8')
                                if not data:
                                    break
                                msg =data.split('|')
                                #print "got message "+data
                                for packet in msg:
                                        fields=packet.split(';')
                                        if len(fields)!=7:
                                                old_data=packet
                                        else :
                                                #self.timer+=1
                                                if self.graphs<1:
                                                        self.outfile.write(packet+'\n')
                                                else:
                                                        qname=fields[1].split(':');
                                                        query_name=qname[0].strip()
                                                        if query_name!=oldquery:
                                                                self.lock.acquire()
                                                                x,y=find(self.queries_list,query_name)
                                                                #print 'got_queries= ',self.got_queries
                                                                if self.got_queries==0 and x==-1:
                                                                        # the query is a new one, not found in the list (x=-1)
                                                                        # and we do not have a predefined list of queries (got_queries=0)
                                                                        # then we add the query to the list
                                                                        # we keep a counter for the list in queries_list where we added the last one
                                                                        # and we add the query to the following, wrapping around when we reach the number of queries specified as a param
                                                                        #print 'got data for query ',query_name
                                                                        l1=len(self.queries_list[0])
                                                                        #print('first set len=',l1)
                                                                        ind=0
                                                                        for l2 in range(len(self.queries_list)):
                                                                                if len(self.queries_list[l2])<l1:
                                                                                        ind=l2
                                                                                        break
                                                                        #print 'will add query to set ',ind
                                                                        self.queries_list[ind].append(query_name)
                                                                        self.timer_init1=0
                                                                        self.timer=0
                                                                        x=1
                                                                self.lock.release()
                                                                #print self.queries_list,"from pid=", fields[2]
                                                        #print "query name="+query_name,self.timer_init1,x,self.timer
                                                        if self.outfile:
                                                                self.outfile.write(packet+'\n')
                                                        if self.timer==self.timer_init1 and self.timer_init1!=-1 and x!=-1:
                                                                self.dqueue_query.put((query_name))
                                                                oldquery=query_name
                                                        elif oldquery!=query_name and self.timer_init1!=-1 and x!=-1:
                                                                self.dqueue_query.put((query_name))
                                                                oldquery=query_name
                                                                self.timer_init1=0
                                                                self.timer=1
                                                        if self.timer_init1>-1 and x!=-1:
                                                                #delt=datetime.timedelta(microseconds=int(fields[4]))
                                                                #dt=d+delt
                                                                self.dqueuedata.put((query_name,int(fields[4]),self.timer))
                                                        self.timer+=1
                        except socket.timeout:
                                #print 'handler ',threading.current_thread(),' is checking if asked to stop'
                         #       if self.stopped():
                                        listen=1
                        except socket.error:
                                #print 'handler ',threading.current_thread(),' is checking if asked to stop'
                                listen=0
                #print 'handler ',threading.current_thread(),' is quitting'
                self.clientsock.close()

class Listener(threading.Thread):
        def __init__(self, serversock,dqueue_query, dqueue, outfile,queries_list,graphs_p,got_queries_p, lock_p):
                if got_queries_p>0:
                        self.got_queries=1
                        self.timer_init=1
                else:
                        self.got_queries=0
                        self.timer_init=-1
                self.serversock=serversock
                self.dqueue_query=dqueue_query
                self.dqueue=dqueue
                self.outfile=outfile
                self.graphs_v=graphs_p
                self.lock=lock_p
                self.serversock.settimeout(1)
                #self._stop = threading.Event()
                self.queries_list=queries_list
                threading.Thread.__init__(self)
        def stopit(self):
                #self._stop.set()
                for i in self.threads_h:
                                #print 'handler ',i,' will be checked if alive'
                                if i.isAlive():
                                        #print 'it is alive, so will be asked to stop'
                                        i.stopit()

        def run(self):
                i=0
                listen=1
                self.threads_h=[]
                print('waiting for connection...')
                while listen:
                        try:

                                clientsock, addr = self.serversock.accept()
                                print('...connected from:', addr)
                                self.threads_h.append(handler(clientsock, addr,self.timer_init, self.dqueue_query, self.dqueue, self.outfile,self.queries_list,self.got_queries,self.graphs_v, self.lock ))
                                self.threads_h[-1].daemon=True
                                self.threads_h[-1].start()
                                #i+=1
                        except socket.timeout:
                                #if self._stop.isSet():
                                        listen=1
                #print 'we have ',len(self.threads_h),' handlers'
                for i in self.threads_h:
                                #print 'handler ',i,' will be checked if alive'
                                if i.isAlive():
                                        #print 'it is alive, so will be asked to stop'
                                        i.stopit()
                print('listener is quitting')


class AppForm(QtGui.QMainWindow):
        def __init__(self,host_p,port_p,queries_p,outfilename_p,queries_list,graphs_p,parent=None,):
                QtGui.QMainWindow.__init__(self, parent)
                self.queries=queries_p
                self.port=port_p
                self.HOST=host_p
                self.outfilename=outfilename_p
                self.threads_h=[]
                self.graphs=graphs_p
                self.lock=threading.Lock()

                self.BUFSIZ = 1250
                self.ADDR = (self.HOST, self.port)
                self.ax=dict()
                self.xdata_init=-1
                self.outfile=''
                self.redraw=1
                self.qnames=[]
                self.delta=999999999
                self.slider_xl_label='Show last 1000'
                if self.outfilename:
                    self.outfile=open(self.outfilename,"a")
                self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.serversock.bind(self.ADDR)
                self.serversock.listen(2)
                self.queries_list=queries_list
                self.ql=queries_p
                if self.graphs>0:
                                self.setWindowTitle('RWPBench')
                                self.datasets=collections.defaultdict(list)
                                self.xdata=collections.defaultdict(list)
                                self.avg_window_size=5
                if self.graphs>0:
                        if self.graphs<4:
                                self.lns=self.graphs
                                self.cols=1
                        elif self.graphs==4:
                                self.lns=2
                                self.cols=2
                        elif self.graphs==5 or self.graphs==6:
                                self.lns=3
                                self.cols=2
                        elif self.graphs<10:
                                self.lns=3
                                self.cols=3
                        else:
                                self.lns=3
                                if int(self.graphs/3)*3==self.graphs:
                                        self.cols=int(self.graphs/3)
                                else :
                                        int(self.graphs/3)+1
                self.timer_init=-1
                self.dqueue=queue.Queue()
                self.dqueue_query=queue.Queue()
                self.thread_listener=Listener(self.serversock,self.dqueue_query, self.dqueue, self.outfile,self.queries_list,self.graphs,self.ql, self.lock)
                self.thread_listener.daemon=True
                self.thread_listener.start()
                if self.graphs>-10:
                        self.create_menu()
                        self.create_main_frame()
                #we create a timer that will refresh the plot every second (timersteps are in milliseconds)
                        self.timer=QtCore.QBasicTimer()
                        self.timer.start(1000,self)


        def quit(self):
                self.thread_listener.stopit()
                #self.thread_listener.join()
                sys.exit()

        def set_XLimits(self):
                self.delta=self.slider_xl.value()
                self.slider_xl_label='Show last '+str(self.delta)
                self.redraw=1

        def get_all_from_queue(self, Q):
            ''' generator to yield one after the others all items currently
                in the Queue Q, without any waiting
            '''
            try:
                    while True:
                            yield Q.get_nowait()
            except queue.Empty:
                        raise StopIteration
        def moving_average(self, x, n):
            """
            compute an n period moving average.


            """
            if len(x)<2*n:
                    return x
            x = numpy.asarray(x)
            weights = numpy.ones(n)

            weights /= weights.sum()

            a =  numpy.convolve(x, weights, mode='full')[:len(x)]
            a[:n] = a[n]
            return a

        def get_colors(self, num_colors):
            import colorsys
            colors=[]
            for i in numpy.arange(0., 360., 360. / num_colors):
                hue = i/360.
                lightness = (50 + numpy.random.rand() * 10)/100.
                saturation = (90 + numpy.random.rand() * 10)/100.
                colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
            return colors

        def create_main_frame(self):
                self.main_frame = QtGui.QWidget()
                winWidth = 683
                winHeight = 784

                screen = QtGui.QDesktopWidget().availableGeometry()
                screenCenterX = (screen.width() - winWidth) / 2
                screenCenterY = (screen.height() - winHeight) / 2
                self.main_frame.setGeometry(screenCenterX, screenCenterY, winWidth, winHeight)

                # Create the mpl Figure and FigCanvas objects.
                # 10x74 inches, 100 dots-per-inch
                #
                if self.graphs>0:
                        self.dpi = 100
                        self.fig = matplotlib.pyplot.Figure((10.0, 7.0), dpi=self.dpi)
                        self.fig.subplots_adjust(hspace=.6)
                        self.canvas = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(self.fig)
                        qlayout = QtGui.QHBoxLayout(self.main_frame)
                        self.main_frame.setLayout(qlayout)
                        qscroll = QtGui.QScrollArea(self.main_frame)
                        qscroll.setGeometry(screenCenterX, screenCenterY, winWidth, winHeight)
                        qscroll.setFrameStyle(QtGui.QFrame.NoFrame)
                        qlayout.addWidget(qscroll)
                        qscrollContents = QtGui.QWidget()
                        qscrollLayout = QtGui.QVBoxLayout(qscrollContents)
                        qscroll.setWidget(qscrollContents)
                        #qscrollLayout.setGeometry(QtCore.QRect(0, 0, 1000, 1000))
                        qfigwidget=QtGui.QWidget(qscrollContents)
                        qscroll.setWidgetResizable(True)
                        self.canvas.setParent(qfigwidget)
                        matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg.setSizePolicy(self.canvas,QtGui.QSizePolicy.Expanding,
                                           QtGui.QSizePolicy.Expanding)
                        self.canvas.setMinimumSize(self.canvas.size())
                        for i in range(self.graphs):
                                self.ax[i] = self.fig.add_subplot(self.lns,self.cols,i+1)

                        # Create the navigation toolbar, tied to the canvas
                        #
                        self.mpl_toolbar = matplotlib.backends.backend_qt4agg.NavigationToolbar2QTAgg(self.canvas, qfigwidget)

                        self.draw_button = QtGui.QPushButton("&Quit")
                        self.connect(self.draw_button, QtCore.SIGNAL('clicked()'), self.quit)

                        self.slider_label_xl = QtGui.QLabel(self.slider_xl_label)
                        self.slider_xl = QtGui.QSlider(QtCore.Qt.Horizontal)
                        self.slider_xl.setRange(100, 1000)
                        self.slider_xl.setValue(1000)
                        self.slider_xl.setSingleStep(50)
                        self.slider_xl.setTracking(True)
                        self.slider_xl.setTickInterval(100)
                        self.slider_xl.setTickPosition(QtGui.QSlider.TicksBothSides)
                        self.connect(self.slider_xl, QtCore.SIGNAL('valueChanged(int)'), self.set_XLimits)

                        #
                        # Layout with box sizers
                        #
                        hbox = QtGui.QHBoxLayout()

                        for w in [self.draw_button, self.slider_label_xl,self.slider_xl]:
                                hbox.addWidget(w)
                                hbox.setAlignment(w, QtCore.Qt.AlignVCenter)
                        vbox = QtGui.QVBoxLayout()
                        vbox.addWidget(self.canvas)
                        vbox.addWidget(self.mpl_toolbar)
                        qfigwidget.setLayout(vbox)
                        qscrollLayout.addWidget(qfigwidget)
                        qscrollLayout.addLayout(hbox)
                        qscrollContents.setLayout(qscrollLayout)
                        self.setCentralWidget(self.main_frame)
                else:
                        self.setCentralWidget(self.main_frame)
        def timerEvent(self, e):
                self.draw()

        def save_plot(self):
                file_choices = "PNG (*.png)|*.png"

                path = str(QtGui.QFileDialog.getSaveFileName(self,
                                'Save file', '',
                                file_choices))
                if path:
                    self.canvas.print_figure(path, dpi=self.dpi)

        def create_menu(self):
                self.file_menu = self.menuBar().addMenu("&Actions")
                quit_action = self.create_action("&Quit", slot=self.quit,
                    shortcut="Ctrl+Q", tip="Close the application")
                if self.graphs>0:
                        load_file_action = self.create_action("&Save plots",
                            shortcut="Ctrl+S", slot=self.save_plot,
                            tip="Save the plots")
                        self.add_actions(self.file_menu,
                            (load_file_action, None, quit_action))
                else:
                        self.add_actions(self.file_menu,
                            (None,quit_action))

        def add_actions(self, target, actions):
                for action in actions:
                    if action is None:
                        target.addSeparator()
                    else:
                        target.addAction(action)

        def create_action(  self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
                action = QtGui.QAction(text, self)
                if icon is not None:
                    action.setIcon(QtGui.QIcon(":/%s.png" % icon))
                if shortcut is not None:
                    action.setShortcut(shortcut)
                if tip is not None:
                    action.setToolTip(tip)
                    action.setStatusTip(tip)
                if slot is not None:
                    self.connect(action, QtCore.SIGNAL(signal), slot)
                if checkable:
                    action.setCheckable(True)
                return action

        def draw(self):
                        if self.graphs>0:
                                self.slider_label_xl.setText(self.slider_xl_label)
                        data=list(self.get_all_from_queue(self.dqueue_query))
                        if len(data)>0:
                                for  j in range(len(data)):
                                        #line_legend[data[j][0]]=data[j][1]
                                        #print self.qnames
                                        if not(data[j] in self.qnames):
                                                self.qnames.append(data[j])
                        data=list(self.get_all_from_queue(self.dqueue))
                        if len(data)>0:
                                for j in range(len(data)):
                                        #print "data[j]=",data[j]
                                        #self.datasets[data[j][0]].append(data[j][1])
                                        if len(self.xdata[data[j][0]])>0:
                                                if self.xdata[data[j][0]][-1]<data[j][2]:
                                                        self.xdata[data[j][0]].append(data[j][2])
                                                        self.datasets[data[j][0]].append(data[j][1])
                                                else:
                                                        ind=self.xdata[data[j][0]].index(data[j][2])
                                                        print('putting ',data[j][1],' at ',ind,' instead of ',len(self.xdata[data[j][0]]),' for query ',data[j][0])
                                                        self.datasets[data[j][0]][ind]=(data[j][1]+self.datasets[data[j][0]][ind])/2
                                        else:
                                                self.xdata[data[j][0]].append(data[j][2])
                                                self.datasets[data[j][0]].append(data[j][1])

                        if len(data)>0 or self.redraw:
                                yd1=[]
                                self.redraw=0
                                for i in range(len(self.ax)):
                                        self.ax[i].clear();
                                if self.graphs>0:
                                        for j in self.datasets.keys():

                                                ydata=self.datasets[j]
                                                xd=self.xdata[j]
                                                #print j,len(ydata),len(xd)
                                                ydata=self.moving_average(ydata,5)
                                                if self.delta<len(xd):
                                                        xmin=len(xd)-self.delta
                                                        xd=xd[xmin:]
                                                        yd=ydata[xmin:]
                                                else:
                                                        yd=ydata
                                                        xmin=0
                                                #print "queries_list=",queries_list,"ql=",self.ql
                                                # setting ql
                                                qindex,yindex=find(queries_list,j)
                                                #print 'qindex=',qindex,' query=',j
                                                self.ax[qindex].plot(xd,yd, label=j)
                                                self.ax[qindex].set_xlabel('Executions')
                                                self.ax[qindex].set_ylabel('Microseconds')
                                        if len(data)>0:
                                                for qindex in range(len(self.ax)):
                                                        self.ax[qindex].legend()
                                        self.fig.canvas.draw()
                                        self.canvas.draw()#matplotlib.pyplot.show(block=False)

if __name__=='__main__':

        HOST = get_local_ip()
        port,queries,outfilename,queries_list,graphs=get_args(sys.argv[1:])
        if graphs>0:
                try:
                        import numpy
                        import matplotlib
                        import matplotlib.pyplot
                        import  matplotlib.backends.backend_qt4agg
                        print('imported matplotlibs')
                except ImportError:
                        print('You do not have the required modules for graphing, please do not specify -g ..')
                        print('No graphs will be show, data will be saved to the file')
                        queries=0
                        graphs=0
        app = QtGui.QApplication(sys.argv)
        form = AppForm(HOST,port,queries,outfilename,queries_list,graphs)
        form.show()
        app.exec_()

