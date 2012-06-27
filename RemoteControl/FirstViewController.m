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

static FirstViewController* viewController;
static NSMutableArray* pyOutputList;

- (NSInteger)tableView:(UITableView *)tableView
 numberOfRowsInSection:(NSInteger)section
{
	if(pyOutputList)
		return [pyOutputList count];
	else
		return 0;
}

- (UITableViewCell *)tableView:(UITableView *)tableView
		 cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	
	static NSString *SimpleTableIdentifier = @"SimpleTableIdentifier";
	UITableViewCell *cell = [tableView
							 dequeueReusableCellWithIdentifier:SimpleTableIdentifier];
	if (cell == nil) {
		cell = [[[UITableViewCell alloc]initWithStyle:UITableViewCellStyleDefault
									  reuseIdentifier:SimpleTableIdentifier] autorelease];
	}
	
	NSUInteger row = [indexPath row];
	cell.textLabel.text = [pyOutputList objectAtIndex:row];
	return cell;
}

static PyObject *
stdout_callback(PyObject *self, PyObject *args)
{
    char *str;
    if (!PyArg_ParseTuple(args, "s;stdout_callback requires a string", &str))
		return NULL;

	dispatch_sync(dispatch_get_main_queue(), ^{

		static NSMutableString* buffer = NULL;
		if(buffer == NULL)
			buffer = [[NSMutableString alloc] init];
		int c = 0;
		for (NSString* s in [[NSString stringWithUTF8String:str] componentsSeparatedByString:@"\n"]) {
			if(c++ == 0) {
				[buffer appendString:s];
				continue;
			}

			printf("Py: %s\n", [buffer UTF8String]);
			
			[pyOutputList addObject:[NSString stringWithString:buffer]];
			//[viewController->pyOutput reloadData];
			UITableView* pyOutput = viewController->pyOutput;
			
			[pyOutput beginUpdates];
			NSArray *indexPaths = [NSArray arrayWithObjects: 
								   [NSIndexPath indexPathForRow:[pyOutputList count]-1 inSection:0],
								   nil];
			[pyOutput insertRowsAtIndexPaths:indexPaths withRowAnimation:UITableViewRowAnimationAutomatic];
			[pyOutput endUpdates];
			[pyOutput scrollToRowAtIndexPath:[indexPaths objectAtIndex:0] atScrollPosition:UITableViewScrollPositionTop animated:YES];
			
			[buffer setString:s];
		}
	});
	
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
	
	PyObject* wrapperObj = PyObject_CallFunctionObjArgs(wrapperClass, NULL);
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
	
	pyOutputList = [[NSMutableArray alloc] init];
	viewController = self;
	
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
