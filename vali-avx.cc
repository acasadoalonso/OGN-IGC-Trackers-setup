#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/types.h>

#include "vali-avx.h"

IGC_Key Key, Key2;

SHA256 HashCalc;

//const char *Message = "Test message for OGN-Tracker crypto-signature - make it a bit longer for SHA512"; // Message to Hash and sign
const int HashLen = 32;                                     // Hash of the message
uint8_t Hash[HashLen]; // = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F };

int main(int argc, char *argv[])

{
  printf("Ver MBEDTLS: %s\n\n", MBEDTLS_VERSION_STRING_FULL);
  int msglen = 100*1024;
  char * Message = (char *) malloc(msglen); 
  char * Temp    = (char *) malloc(msglen); 
  memset(Message, 0, msglen);
  memset(Temp,    0, msglen);
  printf ("IGC File: %s\n", argv[1]);				// name of the file

  FILE *fd0 =fopen(argv[1], "r");				// initially we open as readonly
  if (!fd0)
      {
      printf("Invalid file: %s \n\n ", argv[1]); 
      exit(-1);
      }
  size_t l = fread( Message, msglen, 1, fd0);			// read the file
  l = 0;
  int mlen=strlen(Message);
  printf("Msglen: %d\n", mlen);	// the message is the whole file
  fclose(fd0);							// close as read file
//      now looks for the first G record
  int first = l;
  first = 0;
  int loopidx = mlen;
  while (loopidx > 0)
     {
     if (Message[loopidx] == 'G' && Message[loopidx -1] == '\n')
        {
        if (first != 0)
           break;
        else
           first = loopidx;
        }
     loopidx -= 1;
     }
  char ghash[256];
  memset(ghash, 0, sizeof(ghash));
  memcpy(ghash, Message+loopidx, first - loopidx);
  //printf("G records:\n%s\n%d %d\n%s \n", Message+loopidx, loopidx, first, ghash);
  memcpy(Temp, Message, loopidx);
  //printf("\n%s%d\n", Temp, (int) strlen(Temp));
  
  HashCalc.Init();
  HashCalc.Start();
  HashCalc.Update((const uint8_t *)Temp, strlen(Temp));
  HashCalc.Finish(Hash);
  HashCalc.Free();


  //printf("Message[%d] %s\n", (int)strlen(Message), Message);
  char grec[256];
  memset(grec, 0, sizeof(ghash));
  //printf("Hash[%d] \n", HashLen);
  for(int Idx=0; Idx<HashLen; Idx++)
  { 
     //printf("%02X", Hash[Idx]); 
     sprintf(grec+Idx*2,   "%02X", Hash[Idx]); 
  }
  //printf("\n");
  //printf("%s", grec);
  //printf("\n");
  //printf("%s", ghash);
  if (memcmp(grec, ghash+1, strlen(grec)) == 0)
     printf ("\nOK\n");


  return 0; }

