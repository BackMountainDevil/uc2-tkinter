// ----------- ----------- ----------- ----------- ----------- -----------
// ESP32 script to accept MQTT commands for UC2-control
// by: Rene Lachmann
// date: 11.09.2019
// based on Arduino-Interface by Rene Lachmann, Xavier Uwurukundu
//----------- ----------- ----------- ----------- ----------- -----------
// 2020-09-18 revise Kearney
// ----------------------------------------------------------------------------------------------------------------
//                          INCLUDES
#include <WiFi.h>
#include <PubSubClient.h>
#include <string.h>
#include <vector>
#include <CheapStepper.h>
#include <ctime>
#include <sstream>
// ----------------------------------------------------------------------------------------------------------------
//                          Global Defines
#define MAX_CMD 3
#define MAX_INST 10
#define NCOMMANDS 15
#define MAX_MSG_LEN 40
#define LED_FLUO_PIN 26
// ----------------------------------------------------------------------------------------------------------------
//                          Parameters
// ~~~~ Device ~~~~
// create Pseudo-random number with temporal dependent input

// saved in strings, so that later (if implemented) e.g. easily changeable via Bluetooth -> to avoid connection errors
std::string SETUP = "S001";    //"S013";      //S006->Aurelie; S004->Barbora
std::string COMPONENT = "MOT01"; // LAR01 //LED01 // MOT02=x,y // MOT01=z
std::string DEVICE = "ESP32";
std::string DEVICENAME;
std::string CLIENTNAME;
std::string SETUP_INFO;

// ~~~~  Wifi  ~~~~
const char *ssid = "";
const char *password = "";
WiFiClient espClient;
PubSubClient client(espClient);
// ~~~~  MQTT  ~~~~
const char *MQTT_SERVER = "";
const int MQTT_PORT = 1883;
const char *MQTT_CLIENTID;
const char *MQTT_USER;
const char *MQTT_PASS = "23SPE";
const int MQTT_SUBS_QOS = 0;
//const int MAX_CONN = 10; // maximum tries to connect
const unsigned long period = 80000; // 80s
unsigned long time_now = 0;
// topics to listen to
std::string stopicREC = "/" + SETUP + "/" + COMPONENT + "/RECM";
std::string stopicSTATUS = "/" + SETUP + "/" + COMPONENT + "/STAT";
std::string stopicANNOUNCE = "/" + SETUP + "/" + COMPONENT + "/ANNO";
// Deliminators for CMDs (published via payload-string)
const char *delim_inst = "+";
const int delim_len = 1;

// ~~~~??MOTOR ~~~~
CheapStepper stepperZ (25,26,27,14); 
// ~~~~ FLUO ~~~~
int led_fluo_pwm_frequency = 12000;
int led_fluo_pwm_channel = 0;
int led_fluo_pwm_resolution = 8;

// ~~~~ Commands ~~~~
const char *CMD;     //Commands like: PXL -> limited to size of 3?
int *INST[MAX_INST]; //Maximum number of possible instructions =
std::vector<int> INSTS;
std::string CMDS;

const char *COMMANDSET[NCOMMANDS] = {"DRVX", "DRVY", "DRVZ", "FLUO"};
const char *INSTRUCTS[NCOMMANDS] = {"1", "1", "1", "1"};

// ~~~~ FLUO ~~~~
int FLUO_STATUS = 0;
// ----------------------------------------------------------------------------------------------------------------
//                          Additional Functions
// Most stable and efficient way to have the ESP32 be active for input, but still wait (best for Android as well)
void uc2wait(int period)
{
    unsigned long time_now = millis();
    while (millis() < time_now + period)
    {
        //wait approx. [period] ms
    };
}


void setup_device_properties()
{
    //std::time_t result = std::time(nullptr);
    //srand(result); // init randomizer with pseudo-random seed on boot
    //int randnum = rand() % 10000;
    int rand_number = random(1, 100000);
    std::stringstream srn;
    srn << rand_number;
    DEVICENAME = DEVICE + "_" + srn.str(); // random number generated up to macro MAX_RAND
    CLIENTNAME = SETUP + "_" + COMPONENT + "_" + DEVICENAME;
    SETUP_INFO = "This is:" + DEVICENAME + " on /" + SETUP + "/" + COMPONENT + ".";
    MQTT_CLIENTID = DEVICENAME.c_str(); //"S1_MOT2_ESP32"
    //Serial.print("MQTT_CLIENTID=");Serial.println(MQTT_CLIENTID);
    MQTT_USER = DEVICE.c_str();
    Serial.println(SETUP_INFO.c_str());
}

void setup_wifi()
{
    // uc2wait(10);
    // We start by connecting to a WiFi network
    Serial.println();
    Serial.print("Device-MAC: ");
    Serial.println(WiFi.macAddress());
    Serial.print("Connecting to ");
    Serial.print(ssid);
    WiFi.setHostname(MQTT_CLIENTID);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        // uc2wait(500);
        delay(100);
        Serial.print(".");
    }

    Serial.println("");
    Serial.print("WiFi connected with IP:");
    Serial.println(WiFi.localIP());
}

int separateMessage(byte *message, unsigned int length)
{

    //Serial.println("Seperating Message.");
    //Serial.print("Message=");
    char messageSep[length];
    for (int myc = 0; myc < length; myc++)
    {
        messageSep[myc] = (char)message[myc];
        //Serial.print(messageSep[myc]);
    }
    messageSep[length] = NULL;
    //Serial.println("");
    Serial.print("Mess=");
    std::string mess(messageSep);
    Serial.println(mess.c_str());
    size_t pos = 0;
    int i = 0;
    bool found_cmd = false;
    while ((pos = mess.find(delim_inst)) != std::string::npos)
    {
        if (!found_cmd)
        {
            //Serial.print("CMD-del@");
            //Serial.println(pos);
            CMDS = mess.substr(0, pos);
            //Serial.print("CMDS=");
            CMD = CMDS.c_str();
            //Serial.println(CMD);
            found_cmd = true;
        }
        else
        {
            INSTS.push_back(atoi(mess.substr(0, pos).c_str()));
            //Serial.print("INST[");
            //Serial.print(i);
            //Serial.print("]=");
            //Serial.println(INSTS[i]);
            i++;
        }
        mess.erase(0, pos + delim_len);
    }
    if (!found_cmd)
    {
        //Serial.print("CMD-del@");
        //Serial.println(pos);
        CMDS = mess.substr(0, pos);
        //Serial.print("CMDS=");
        CMD = CMDS.c_str();
        //Serial.println(CMD);
        found_cmd = true;
    }
    else if (mess.length() > 0)
    {
        INSTS.push_back(atoi(mess.substr(0, pos).c_str()));
        //Serial.print("INST[");
        //Serial.print(i);
        //Serial.print("]=");
        //Serial.println(INSTS[i]);
        i++;
    }
    else
    {
        Serial.println("Nothing found...");
    }
    return i;
    mess.clear();
}

void callback(char *topic, byte *message, unsigned int length)
{
    Serial.println("Callback-func called.");
    // test topics
    if (std::string(topic) == stopicREC)
    {
        int nINST = separateMessage(message, length);
        Serial.print("INSTS[0] ");
        Serial.println(INSTS[0]);
        if (strcmp(CMD, COMMANDSET[0]) == 0)
        {
        }
        else if (strcmp(CMD, COMMANDSET[1]) == 0)
        {
        }
        else if (strcmp(CMD, COMMANDSET[2]) == 0)
        {
            if( INSTS[0]>0){
                Serial.println("CW");
                stepperZ.moveDegreesCW(INSTS[0]);
                Serial.print("step position: ");
                Serial.print(stepperZ.getStep());
                Serial.print(" / 4096");
                Serial.println();
                delay(1000);
            }             
            else{
                Serial.println("CCW");
                stepperZ.moveDegreesCCW(0-INSTS[0]);
                Serial.print("step position: ");
                Serial.print(stepperZ.getStep());
                Serial.print(" / 4096");
                Serial.println();
                delay(1000);
            }
                
            // stepperZ.Move(INSTS[0] * 10);
        }
        else if (strcmp(CMD, COMMANDSET[3]) == 0)
        {

        }
        else
        {
            Serial.print("CMD not found.");
        }
    }
    else if (std::string(topic) == stopicSTATUS)
    {
        Serial.println(stopicSTATUS.c_str());
    }
    else if (std::string(topic) == stopicANNOUNCE)
    {
        Serial.println(stopicANNOUNCE.c_str());
    }
    else
    {
        Serial.print("Assortion Error: Nothing found for topic=");
        Serial.println(topic);
    }
    INSTS.clear();
}

void reconnect()
{
    // Loop until we're reconnected
    while (!client.connected())
    {
        Serial.print("MQTT_CLIENTID=");
        Serial.println(MQTT_CLIENTID);
        Serial.print("topicSTATUS=");
        Serial.println(stopicSTATUS.c_str());
        Serial.print("Attempting MQTT connection...");
        // Attempt to connect

        if (client.connect(MQTT_CLIENTID, stopicSTATUS.c_str(), 2, 1, "0"))
        {
            // client.connect(MQTT_CLIENTID,MQTT_USER,MQTT_PASS,"esp32/on",2,1,"off")
            Serial.println("connected");
            // Subscribe
            client.subscribe(stopicREC.c_str());
            client.publish(stopicSTATUS.c_str(), "1");
            client.publish(stopicANNOUNCE.c_str(), SETUP_INFO.c_str());
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            // Wait 5 seconds before retrying
            uc2wait(5000);
        }
    }
}

// ----------------------------------------------------------------------------------------------------------------
//                          SETUP
void setup()
{
    Serial.begin(115200);
    // check for connected motors
    //status = bme.begin();
    setup_device_properties();
    Serial.print("VOID SETUP -> topicSTATUS=");
    Serial.println(stopicSTATUS.c_str());
    setup_wifi();
    Serial.print("Starting to connect MQTT to: ");
    Serial.print(MQTT_SERVER);
    Serial.print(" at port:");
    Serial.println(MQTT_PORT);
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback(callback);
    time_now = millis();
    stepperZ.setRpm(15);
}
// ----------------------------------------------------------------------------------------------------------------
//                          LOOP
void loop()
{
    if (!client.connected())
    {
        reconnect();
    }
    client.loop();
    if (time_now + period < millis())
    {
        client.publish(stopicSTATUS.c_str(), "1");
        time_now = millis();
    }
}
// ----------------------------------------------------------------------------------------------------------------
