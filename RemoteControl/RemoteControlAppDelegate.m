//
//  RemoteControlAppDelegate.m
//  RemoteControl
//
//  Created by Albert Zeyer on 14.03.11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "RemoteControlAppDelegate.h"
#include "Python.h"

@implementation RemoteControlAppDelegate


@synthesize window=_window;

@synthesize tabBarController=_tabBarController;

static PyObject *
webbrowser_open(PyObject *self, PyObject *args)
{
    char *str;
	
    if (!PyArg_ParseTuple(args,
						  "s;open requires a string",
                          &str)) {
		return NULL;
    }
	
	printf("webbrowser iOS open '%s'\n", str);
	
	NSURL *url = [NSURL URLWithString:[NSString stringWithUTF8String:str]];
	[[UIApplication sharedApplication] openURL:url];

    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(webbrowser_open_doc, "open(url)");

static PyMethodDef webbrowser_methods[] = {
    {"open",           webbrowser_open, METH_VARARGS, webbrowser_open_doc},
    {NULL,              NULL}           /* sentinel */
};
PyDoc_STRVAR(module_doc, "iOS specific webbrowser module");

void initioswebbrowser(void) {
    PyObject *m;
	
    /* Create the module and add the functions and documentation */
    m = Py_InitModule3("webbrowser", webbrowser_methods, module_doc);
    if (m == NULL)
        return;
}

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
	Py_SetProgramName((char*)[[[[NSBundle mainBundle] bundlePath] stringByAppendingString:@"/"] UTF8String]);
	PyImport_AppendInittab("webbrowser", initioswebbrowser);
	Py_Initialize();
	
	PyRun_SimpleString("print 'hello there'");

	// Override point for customization after application launch.
	// Add the tab bar controller's current view as a subview of the window
	self.window.rootViewController = self.tabBarController;
	[self.window makeKeyAndVisible];
	
    return YES;
}

- (void)applicationWillResignActive:(UIApplication *)application
{
	/*
	 Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
	 Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.
	 */
}

- (void)applicationDidEnterBackground:(UIApplication *)application
{
	/*
	 Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later. 
	 If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
	 */
}

- (void)applicationWillEnterForeground:(UIApplication *)application
{
	/*
	 Called as part of the transition from the background to the inactive state; here you can undo many of the changes made on entering the background.
	 */
}

- (void)applicationDidBecomeActive:(UIApplication *)application
{
	/*
	 Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
	 */
}

- (void)applicationWillTerminate:(UIApplication *)application
{
	/*
	 Called when the application is about to terminate.
	 Save data if appropriate.
	 See also applicationDidEnterBackground:.
	 */
}

- (void)dealloc
{
	[_window release];
	[_tabBarController release];
    [super dealloc];
}

/*
// Optional UITabBarControllerDelegate method.
- (void)tabBarController:(UITabBarController *)tabBarController didSelectViewController:(UIViewController *)viewController
{
}
*/

/*
// Optional UITabBarControllerDelegate method.
- (void)tabBarController:(UITabBarController *)tabBarController didEndCustomizingViewControllers:(NSArray *)viewControllers changed:(BOOL)changed
{
}
*/

@end
