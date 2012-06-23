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

// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad
{
    [super viewDidLoad];
	
	printf("viewDidLoad\n");
	[playButton setHidden:TRUE];

	dispatch_queue_t backgroundQueue = dispatch_queue_create("loadPyton", 0);

	dispatch_async(backgroundQueue, ^{
		NSString* mainPyFile = [[[NSBundle mainBundle] bundlePath] stringByAppendingString:@"/py/client/client.py"];
		FILE* fp = fopen([mainPyFile UTF8String], "r");
		PyRun_SimpleFile(fp, [mainPyFile UTF8String]);
		
        dispatch_sync(dispatch_get_main_queue(), ^{
			[playButton setHidden:FALSE];
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

- (IBAction)playPressed { PyRun_SimpleString("doControl('play')"); }
- (IBAction)prevPressed { PyRun_SimpleString("doControl('previous')"); }
- (IBAction)nextPressed { PyRun_SimpleString("doControl('next')"); }
- (IBAction)volUpPressed { PyRun_SimpleString("doControl('sound_up')"); }
- (IBAction)volDownPressed { PyRun_SimpleString("doControl('sound_down')"); }
- (IBAction)reconnectPressed { PyRun_SimpleString("doReconnect()"); }

@end
