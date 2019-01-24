from typing import *
from Filter import Filter
from SingleIndex import SingleIndex
from Attributes import Attribute

class Add(Filter):
    def __init__(self):
        super().__init__()
        self.m_AttributeType=Attribute.NUMERIC
        self.m_Name="unnamed"
        self.m_Insert=SingleIndex("last")
        self.m_Labels=[]
        self.m_DateFormat="%Y-%m-%d'T'%H:%M:%S"
        self.m_Weight=1

    def listOptions(self):
        newVector=[]
        desc;
        SelectedTag
        tag;
        int
        i;

        newVector = new
        Vector < Option > ();

        desc = "";
        for (i = 0; i < TAGS_TYPE.length; i++) {
        tag = new SelectedTag(TAGS_TYPE[i].getID(), TAGS_TYPE);
        desc += "\t" + tag.getSelectedTag().getIDStr() + " = "
        + tag.getSelectedTag().getReadable() + "\n";
        }
        newVector.addElement(new
        Option("\tThe type of attribute to create:\n"
               + desc + "\t(default: " + new
        SelectedTag(Attribute.NUMERIC, TAGS_TYPE)
        + ")", "T", 1, "-T " + Tag.toOptionList(TAGS_TYPE)));

        newVector.addElement(new
        Option(
            "\tSpecify where to insert the column. First and last\n"
            + "\tare valid indexes.(default: last)", "C", 1, "-C <index>"));

        newVector.addElement(new
        Option("\tName of the new attribute.\n"
               + "\t(default: 'Unnamed')", "N", 1, "-N <name>"));

        newVector.addElement(new
        Option(
            "\tCreate nominal attribute with given labels\n"
            + "\t(default: numeric attribute)", "L", 1, "-L <label1,label2,...>"));

        newVector.addElement(new
        Option(
            "\tThe format of the date values (see ISO-8601)\n"
            + "\t(default: yyyy-MM-dd'T'HH:mm:ss)", "F", 1, "-F <format>"));

        newVector.addElement(new
        Option(
            "\tThe weight for the new attribute\n"
            + "\t(default: 1.0)", "W", 1, "-W <double>"));

        return newVector.elements();