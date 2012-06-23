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

/*
// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad
{
    [super viewDidLoad];
}
*/

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
