from typing import *
from Filter import Filter
from SingleIndex import SingleIndex
from Attributes import Attribute
from SelectedTag import SelectedTag
from Option import Option
from Tag import Tag
from Instances import Instances
from Utils import Utils
from OptionHandler import OptionHandler

class Add(Filter,OptionHandler):
    TAGS_TYPE=[Tag(Attribute.NUMERIC,"NUM","Numeric attribute"),
               Tag(Attribute.NOMINAL,"NOM","Nominal attribute"),
               Tag(Attribute.STRING,"STR","String attribute"),
               Tag(Attribute.DATE,"DAT","Date attribute")]

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
        desc=""

        for i in  range(len(self.TAGS_TYPE)):
            tag=SelectedTag(self.TAGS_TYPE[i].getID(),self.TAGS_TYPE)
            desc+="\t"+tag.getSelectedTag().getIDStr()+" = "+tag.getSelectedTag().getReadable()+"\n"

        newVector.append(Option("\tThe type of attribute to create:\n"+ desc + "\t(default: " + str(SelectedTag(Attribute.NUMERIC, self.TAGS_TYPE))
                                 + ")", "T", 1, "-T " + Tag.toOptionList(self.TAGS_TYPE)))
        newVector.append(Option("\tSpecify where to insert the column. First and last\n" + "\tare valid indexes.(default: last)", "C", 1, "-C <index>"))
        newVector.append(Option("\tName of the new attribute.\n" + "\t(default: 'Unnamed')", "N", 1, "-N <name>"))
        newVector.append(Option("\tCreate nominal attribute with given labels\n" + "\t(default: numeric attribute)", "L", 1, "-L <label1,label2,...>"))
        newVector.append(Option("\tThe format of the date values (see ISO-8601)\n" + "\t(default: yyyy-MM-dd'T'HH:mm:ss)", "F", 1, "-F <format>"))
        newVector.append(Option("\tThe weight for the new attribute\n" + "\t(default: 1.0)", "W", 1, "-W <double>"))
        return newVector

    def setOption(self,options:List[str]):
        tmpStr=Utils.getOption('T',options)
        if len(tmpStr) != 0:
            self.setAttributeType(SelectedTag(tmpStr,self.TAGS_TYPE))
        else:
            self.setAttributeType(SelectedTag(Attribute.NUMERIC,self.TAGS_TYPE))

        tmpStr=Utils.getOption('C',options)
        if len(tmpStr) == 0:
            tmpStr="last"
        self.setAttributeIndex(tmpStr)
        self.setAttributeName(Utils.unbackQuoteChars(Utils.getOption('N',options)))
        if self.m_AttributeType == Attribute.NOMINAL:
            tmpStr=Utils.getOption('L',options)
            if len(tmpStr) != 0:
                self.setNominalLabels(tmpStr)
        elif self.m_AttributeType == Attribute.DATE:
            tmpStr=Utils.getOption('F',options)
            #TODO  时间格式暂不做修改
            if len(tmpStr) != 0:
                pass
        tmpStr=Utils.getOption('W',options)
        if len(tmpStr) == 0:
            self.setWeight(1.0)
        else:
            self.setWeight(float(tmpStr))
        if self.getInputFormat() is not None:
            self.setInputFormat(self.getInputFormat())



    def getOptions(self)->List[str]:
        result=[]
        if self.m_AttributeType != Attribute.NUMERIC:
            result.append('-T')
            result.append(str(self.getAttributeType()))
        result.append('-N')
        result.append(Utils.backQuoteChars(self.getAttributeName()))
        if self.m_AttributeType == Attribute.NOMINAL:
            result.append('-L')
            result.append(self.getNominalLabels())
            result.append('-F')
            result.append(self.getDateFormat())
        result.append('-C')
        result.append(self.getAttributeIndex())

        result.append('-W')
        result.append(str(self.getWeight()))

        return result


    def getAttributeType(self):
        return SelectedTag(self.m_AttributeType,self.TAGS_TYPE)

    def getWeight(self):
        return self.m_Weight

    def getAttributeName(self):
        return self.m_Name

    def getAttributeIndex(self):
        return self.m_Insert.getSingleIndex()

    def getDateFormat(self):
        return self.m_DateFormat

    def getNominalLabels(self):
        labelList=""
        for i in range(len(self.m_Labels)):
            if i==0:
                labelList=self.m_Labels[i]
            else:
                labelList+=","+self.m_Labels[i]
        return labelList

    def setAttributeType(self,value:SelectedTag):
        if value.getTags() == self.TAGS_TYPE:
            self.m_AttributeType=value.getSelectedTag().getID()

    def setAttributeIndex(self,attrIndex:str):
        self.m_Insert.setSingleIndex(attrIndex)

    def setAttributeName(self,name:str):
        if name.strip()=="":
            self.m_Name="unnamed"
        else:
            self.m_Name=name

    def setNominalLabels(self,labelList:str):
        labels=[]
        commaLoc=labelList.index(',')
        while commaLoc >= 0:
            label=labelList[0:commaLoc].strip()
            if label != "":
                labels.append(label)
            labelList=labelList[commaLoc+1:]
        label=labelList.strip()
        if label != "":
            labels.append(label)

        self.m_Labels=labels
        if len(labels)==0:
            self.m_AttributeType=Attribute.NUMERIC
        else:
            self.m_AttributeType=Attribute.NOMINAL

    def setWeight(self,weight):
        self.m_Weight=weight

    def getInputFormat(self)->Instances:
        return self.m_InputFormat

    def setInputFormat(self,instanceInfo:Instances):
        super().setInputFormat(instanceInfo)
        self.m_Insert.setUpper(instanceInfo.numAttributes())
        outputFormat=Instances(instanceInfo,0)
        newAttribute=None
        if self.m_AttributeType == Attribute.NUMERIC:
            newAttribute=Attribute(self.m_Name)
        elif self.m_AttributeType == Attribute.NOMINAL:
            newAttribute=Attribute(self.m_Name,self.m_Labels)
        elif self.m_AttributeType == Attribute.STRING:
            newAttribute=Attribute(self.m_Name,True)
        elif self.m_AttributeType == Attribute.DATE:
            newAttribute=Attribute(self.m_Name,self.m_DateFormat)
        newAttribute.setWeight(self.getWeight())
        outputFormat.insertAttributeAt(newAttribute,self.m_Insert.getIndex())
        self.setOutputFormat(outputFormat)
        return True

    # def getCapabilities(self):


