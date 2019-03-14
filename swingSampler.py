import javax.swing as swing
import java.awt as awt
import java.net as net
import sys

# https://wiki.python.org/jython/SwingSampler
# I've organized the sampler code into a single class, called SwingSampler.
# The __init__ function (called the "constructor") does all of the setup.
# Note that __init__, like all other functions in a class (called "methods")
# takes "self" as its first argument.
#
class SwingSampler:
        def __init__(self):
                #########################################################
                #
                # set up the overall frame (the window itself)
                #
                self.window = swing.JFrame("Swing Sampler!")
                self.window.windowClosing = self.goodbye
                self.window.contentPane.layout = awt.BorderLayout()

                #########################################################
                #
                # under this will be a tabbed pane; each tab is named
                # and contains a panel with other stuff in it.
                #
                tabbedPane = swing.JTabbedPane()
                self.window.contentPane.add("Center", tabbedPane);

                #########################################################
                #
                # The first tabbed panel will be named "Some Basic
                # Widgets", and is referenced by variable 'firstTab'
                #
                firstTab = swing.JPanel()
                firstTab.layout = awt.BorderLayout()
                tabbedPane.addTab("Some Basic Widgets", firstTab)

                #
                # slap in some labels, a list, a text field, etc... Some
                # of these are contained in their own panels for
                # layout purposes.
                #
                tmpPanel = swing.JPanel()
                tmpPanel.layout = awt.GridLayout(3, 1)
                tmpPanel.border = swing.BorderFactory.createTitledBorder("Labels are simple")
                tmpPanel.add(swing.JLabel("I am a label. I am quite boring."))
                tmpPanel.add(swing.JLabel("<HTML><FONT COLOR='blue'>HTML <B>labels</B></FONT> are <I>somewhat</I><U>less boring</U>.</HTML>"))
                tmpPanel.add(swing.JLabel("Labels can also be aligned", swing.JLabel.RIGHT))
                firstTab.add(tmpPanel, "North")

                #
                # Notice that the variable "tmpPanel" gets reused here.
                # This next line creates a new panel, but we reuse the
                # "tmpPanel" name to refer to it.  The panel that
                # tmpPanel used to refer to still exists, but we no
                # longer have a way to name it (but that's ok, since
                # we don't need to refer to it any more).
                #
                tmpPanel = swing.JPanel()
                tmpPanel.layout = awt.BorderLayout()
                tmpPanel.border = swing.BorderFactory.createTitledBorder("Tasty tasty lists")

                #
                # Note that here we stash a reference to the list in
                # "self.list".  This puts it in the scope of the object,
                # rather than this function.  This is because we'll be
                # referring to it later from outside this function, so
                # it needs to be "bumped up a level."
                # 
                self.listData = ( "January", "February", "March", "April", "May", "June", "July", 
                                  "August", "September", "October", "November", "December" )            
                self.list = swing.JList(self.listData)
                tmpPanel.add("Center", swing.JScrollPane(self.list))
                button = swing.JButton("What's Selected?")
                button.actionPerformed = self.whatsSelectedCallback;
                tmpPanel.add("East", button)
                firstTab.add("Center", tmpPanel)

                tmpPanel = swing.JPanel()
                tmpPanel.layout = awt.BorderLayout()

                #
                # The text field also goes in self, since the callback
                # that displays the contents will need to get at it.
                # 
                # Also note that because the callback is a function inside
                # the SwingSampler object, you refer to it through self.
                # (The callback could potentially be outside the object,
                # as a top-level function. In that case you wouldn't
                # use the 'self' selector; any variables that it uses
                # would have to be in the global scope.
                #
                self.field = swing.JTextField()
                tmpPanel.add(self.field)
                tmpPanel.add(swing.JButton("Click Me", actionPerformed=self.clickMeCallback), "East")
                firstTab.add(tmpPanel, "South")

                #########################################################
                #
                # The second tabbed panel is next...  This shows
                # how to build a basic web browser in about 20 lines.
                #
                secondTab = swing.JPanel()
                secondTab.layout = awt.BorderLayout()
                tabbedPane.addTab("HTML Fanciness", secondTab)

                tmpPanel = swing.JPanel()
                tmpPanel.add(swing.JLabel("Go to:"))
                self.urlField = swing.JTextField(40, actionPerformed=self.goToCallback)
                tmpPanel.add(self.urlField)
                tmpPanel.add(swing.JButton("Go!", actionPerformed=self.goToCallback))
                secondTab.add(tmpPanel, "North")

                #self.htmlPane = swing.JEditorPane("http://www.cc.gatech.edu", editable=0,                hyperlinkUpdate=self.followHyperlink, preferredSize=(400, 400))
                self.htmlPane = swing.JEditorPane("http://www.jython.org", editable=0, 
                                        hyperlinkUpdate=self.followHyperlink, preferredSize=(400, 400))
                secondTab.add(swing.JScrollPane(self.htmlPane), "Center")

                self.statusLine = swing.JLabel("")

                #########################################################
                #
                # The third tabbed panel is next... 
                #
                thirdTab = swing.JPanel()
                tabbedPane.addTab("Other Widgets", thirdTab)

                imageLabel = swing.JLabel(swing.ImageIcon(net.URL("http://www.gatech.edu/images/logo-gatech.gif")))
                imageLabel.toolTipText = "Labels can have images! Every widget can have a tooltip!"
                thirdTab.add(imageLabel)

                tmpPanel = swing.JPanel()
                tmpPanel.layout = awt.GridLayout(3, 2)
                tmpPanel.border = swing.BorderFactory.createTitledBorder("Travel Checklist")
                tmpPanel.add(swing.JCheckBox("Umbrella", actionPerformed=self.checkCallback))
                tmpPanel.add(swing.JCheckBox("Rain coat", actionPerformed=self.checkCallback))
                tmpPanel.add(swing.JCheckBox("Passport", actionPerformed=self.checkCallback))
                tmpPanel.add(swing.JCheckBox("Airline tickets", actionPerformed=self.checkCallback))
                tmpPanel.add(swing.JCheckBox("iPod", actionPerformed=self.checkCallback))
                tmpPanel.add(swing.JCheckBox("Laptop", actionPerformed=self.checkCallback))
                thirdTab.add(tmpPanel)

                tmpPanel = swing.JPanel()
                tmpPanel.layout = awt.GridLayout(4, 1)
                tmpPanel.border = swing.BorderFactory.createTitledBorder("My Pets")
                #
                # A ButtonGroup is used to indicate which radio buttons
                # go together.
                #
                buttonGroup = swing.ButtonGroup()

                radioButton = swing.JRadioButton("Dog", actionPerformed=self.radioCallback)
                buttonGroup.add(radioButton)
                tmpPanel.add(radioButton)

                radioButton = swing.JRadioButton("Cat", actionPerformed=self.radioCallback)
                buttonGroup.add(radioButton)
                tmpPanel.add(radioButton)
                
                radioButton = swing.JRadioButton("Pig", actionPerformed=self.radioCallback)
                buttonGroup.add(radioButton)
                tmpPanel.add(radioButton)

                radioButton = swing.JRadioButton("Capybara", actionPerformed=self.radioCallback)
                buttonGroup.add(radioButton)
                tmpPanel.add(radioButton)

                thirdTab.add(tmpPanel)
        
                self.window.pack()
                self.window.show()

        #
        # This is the callback that's run when the window closes.  Here
        # we just exit.  Note that either functions inside class
        # declarations or global functions can be callbacks.  When they're
        # inside a class they talk 'self' as the first argument.  Just
        # about all Swing callbacks also take an event argument as well.
        #
        def goodbye(self, event):
                print "Goodbye!"
                sys.exit()

        #
        # Callback for the "Click Me!" button on the first tab.  This
        # creates a new window to display what was in the text field,
        # and then clears the text field.
        #
        def clickMeCallback(self, event):
                dialog = swing.JFrame("You clicked the button!")
                dialog.contentPane.layout = awt.BorderLayout()
                dialog.contentPane.add(swing.JLabel("Text was: " + self.field.text))
                dialog.size=(400, 200)
                dialog.show()
                print "Text is ", self.field.text
                self.field.text = ""

        #
        # Callback for the "What's Selected?" button. This pops up a
        # window that shows the contents and index of the selected item.
        #
        def whatsSelectedCallback(self, event):
                dialog = swing.JFrame("Here's what's selected")
                dialog.contentPane.layout = awt.GridLayout(2, 1)
                dialog.contentPane.add(swing.JLabel("Selected value = " + str(self.list.selectedValue),
                                       swing.JLabel.CENTER))
                dialog.contentPane.add(swing.JLabel("Selected index = " + str(self.list.selectedIndex), 
                                       swing.JLabel.CENTER))
                dialog.size=(400, 200)
                dialog.show()
                print "Selected value =", self.list.selectedValue, ", selected index =", self.list.selectedIndex;

        #
        # Callback for the "Go To" button; updates the contents of the
        # HTML pane.
        #
        def goToCallback(self, event):
                self.htmlPane.setPage(self.urlField.text)

        #
        # This callback is invoked whenever a link is clicked or moused
        # over.  The event is a HyperlinkEvent, which means that it
        # defines certain fields and operations, which we can use below.
        #       
        def followHyperlink(self, event):
                if event.eventType == swing.event.HyperlinkEvent.EventType.ACTIVATED:
                        self.statusLine = event.URL.toString()
                        self.htmlPane.setPage(event.URL)
                elif event.eventType == swing.event.HyperlinkEvent.EventType.ENTERED:
                        self.statusLine = event.URL.toString()
                elif event.eventType == swing.event.HyperlinkEvent.EventType.EXITED:
                        self.statusLine = ""

        #
        # This is a common technique when a bunch of widgets share a
        # single callback.  You can look at the "source" field on the
        # event argument to see which widget generated the event.
        #
        def checkCallback(self, event):
                if event.source.selected:
                        print event.source.text + " was CHECKED"
                else:
                        print event.source.text + " was UNCHECKED"

        # 
        # This is the callback for all the radio buttons.
        #
        def radioCallback(self, event):
                print event.source.text + " was clicked ON"


#
# This is how you make the main entry point for your program in Python.
# The system variable __name__ will be set to the string __main__ if
# this file is passed directly on the command line to Jython.  
#
# Here, we simply create a SwingSampler, and it does everything from
# there.
#
if __name__ == "__main__":
        sampler = SwingSampler()