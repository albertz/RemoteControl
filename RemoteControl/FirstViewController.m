//
//  FirstViewController.m
//  RemoteControl
//
//  Created by Albert Zeyer on 14.03.11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "FirstViewController.h"
#include "Python.h"

@implementation FirstViewController

static PyObject *
stdout_callback(PyObject *self, PyObject *args)
{
    char *str;
	
    if (!PyArg_ParseTuple(args,
						  "s;stdout_callback requires a string",
                          &str)) {
		return NULL;
    }
	
	for (NSString* s in [[NSString stringWithUTF8String:str] componentsSeparatedByString:@"\n"]) {
		printf("Py: %s\n", str);
	}
	
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef StdoutWrapperMethods[] =
{
    {"write", stdout_callback, METH_VARARGS, ""},
    {"writeline", stdout_callback, METH_VARARGS, ""},
    {0, 0},
};

void initStdoutWrapper()
{
    PyObject *classDict = PyDict_New();
    PyObject *className = PyString_FromString("StdoutWrapper");
    PyObject *wrapperClass = PyClass_New(NULL, classDict, className);
    Py_DECREF(classDict);
    Py_DECREF(className);
		
	PyObject* wrapperObj = PyEval_CallFunction(wrapperClass, "");
    Py_DECREF(wrapperClass);

    /* add methods to object */
    for (PyMethodDef* def = StdoutWrapperMethods; def->ml_name != NULL; def++) {
        PyObject *func = PyCFunction_New(def, NULL);
        //PyObject *method = PyMethod_New(func, NULL, wrapperClass);
        PyObject_SetAttrString(wrapperObj, def->ml_name, func);
        Py_DECREF(func);
        //Py_DECREF(method);
    }
	
	PySys_SetObject("stdout", wrapperObj);
	Py_DECREF(wrapperObj);
}

// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad
{
    [super viewDidLoad];
	
	printf("viewDidLoad\n");
	initStdoutWrapper();
	
	UIActivityIndicatorView *date  = [[UIActivityIndicatorView alloc] initWithFrame:CGRectMake(150, 150, 30, 30)];
	[date setActivityIndicatorViewStyle:UIActivityIndicatorViewStyleGray];
	[[self view] addSubview:date];
	[date startAnimating];
	

	dispatch_queue_t backgroundQueue = dispatch_queue_create("loadPyton", 0);

	dispatch_async(backgroundQueue, ^{
		[UIApplication sharedApplication].networkActivityIndicatorVisible = YES;
 		NSString* mainPyFile = [[[NSBundle mainBundle] bundlePath] stringByAppendingString:@"/py/client/client.py"];
		FILE* fp = fopen([mainPyFile UTF8String], "r");
		PyRun_SimpleFile(fp, [mainPyFile UTF8String]);
		
        dispatch_sync(dispatch_get_main_queue(), ^{
			[date removeFromSuperview];
			[UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
        });
    });
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}


- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc. that aren't in use.
}


- (void)viewDidUnload
{
    [super viewDidUnload];

    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}


- (void)dealloc
{
    [super dealloc];
}

void doPython(const char* cmd) {
	[UIApplication sharedApplication].networkActivityIndicatorVisible = YES;
	PyRun_SimpleString(cmd);
	[UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
}

void doControl(const char* action) {
	NSString* pyCmd = [NSString stringWithFormat:@"doControl('%s')", action];
	doPython([pyCmd UTF8String]);
}

- (IBAction)playPressed { doControl("play"); }
- (IBAction)prevPressed { doControl("previous"); }
- (IBAction)nextPressed { doControl("next"); }
- (IBAction)volUpPressed { doControl("sound_up"); }
- (IBAction)volDownPressed { doControl("sound_down"); }
- (IBAction)reconnectPressed { doPython("doReconnect()"); }

@end
