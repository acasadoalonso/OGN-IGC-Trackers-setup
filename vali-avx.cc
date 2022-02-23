#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <stdlib.h> 					/* exit, atoi, malloc, free */

#ifdef __linux__ 
    #include <sys/socket.h> 				/* socket, connect */
    #include <netdb.h> 					/* struct hostent, gethostbyname */
    #include <netinet/in.h> 				/* struct sockaddr_in, struct sockaddr */
    #include <unistd.h> 				/* read, write, close */
#elif _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #include <windows.h>
#if !defined(__MINGW32__)
    #pragma comment(lib,"ws2_32.lib") 			//Winsock Library
    #pragma warning(disable : 4996)
#endif
#else

#endif

#include "base64.h"
#include "vali-avx.h"

// ======================================================================================= //
int getregport(void)					// get the registration website port
    {
    int portno = 80;
    return(portno);
    }

char *getreghost(void)					// get the registration website URL
    {
    const char *host = "glidertracking.fai.org";
    return((char *) host);
    }

// ======================================================================================= //

uint8_t 
hextobin(const char * str, uint8_t * bytes, size_t blen)   // Convert string to binary
{
   uint8_t  pos;
   uint8_t  idx0;
   uint8_t  idx1;

   // mapping of ASCII characters to hex values
   const uint8_t hashmap[] =
   {
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, //  !"#$%&'
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ()*+,-./
     0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, // 01234567
     0x08, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 89:;<=>?
     0x00, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x00, // @ABCDEFG
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // HIJKLMNO
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // PQRSTUVW
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // XYZ[\]^_
     0x00, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x00, // `abcdefg
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // hijklmno
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // pqrstuvw
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // xyz{|}~.
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // ........
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00  // ........
   };

   memset(bytes, 0, blen);
   for (pos = 0; ((pos < (blen*2)) && (pos < strlen(str))); pos += 2)
   {
      idx0 = (uint8_t)str[pos+0];
      idx1 = (uint8_t)str[pos+1];
      bytes[pos/2] = (uint8_t)(hashmap[idx0] << 4) | hashmap[idx1];
   };

   return(0);
}

// ======================================================================================= //
//
// C program to find the size of file
// 
// ======================================================================================= //

long int 
findSize(char file_name[])
{
    // opening the file in read mode
    FILE* fp = fopen(file_name, "r");
  
    // checking if the file exist or not
    if (fp == NULL) {
        printf("File Not Found!\n");
        return -1;
    }
  
    fseek(fp, 0L, SEEK_END);
  
    // calculating the size of the file
    long int res = ftell(fp);
  
    // closing the file
    fclose(fp);
  
    return res;
}


// -------------------------------------------------------------------- //

void error(const char *msg) { perror(msg); exit(0); }

// -------------------------------------------------------------------- //
//
// Get the data from the FAI registration server 
//
// -------------------------------------------------------------------- //

char *
getregdata(char * output, int outlen, const char *reg, const char *mac, int prt)
{
    const char *devid="12345";
    struct hostent *server;
    struct sockaddr_in serv_addr;
    int received,  message_size;
    char *message, response[4096];
    char *host = getreghost();
    int portno = getregport();
    const char *path = "/registration/V1/index.php";
    const char *data = "?action=getdata";
    //const char *hdr1 = "Accept:Application/json\r\n";
    //const char *hdr2 = "Content-Type:application/json\r\n";
    unsigned char dte[26]  = "";

    char  * nonce;
    size_t  noncel = 0  ;
    char    nonceurl[64];
    memset  (nonceurl, 0, sizeof(nonceurl));
    time_t timer;
    struct tm* tm_info;

    timer = time(NULL);
    tm_info = localtime(&timer);
    tm_info = gmtime(&timer);

    strftime((char *) dte, 12, "%Y-%m-%d", tm_info);	// prepare the nonce as a safeguard of the URL
    nonce = base64_encode(dte, 10, &noncel);		// encoded as base64
    url_encoder_rfc_tables_init();			// init the encode
    url_encode(html5, (unsigned char *)nonce, nonceurl);// convert it to a format acceptable by the URL
    *(nonce+16) = '\0';					// terminate the stringn
    							/* How big is the message? */
    message_size=outlen;
    message =(char *) malloc(message_size);		// get a work area
    memset(message, 0, message_size);			// clean it
    memset(output,  0, outlen);				// clean it
							// prepare the full URL to get the content of the registration data
    sprintf(message, "GET %s%s&registration=%s&mac=%s&devid=%s&token=%s HTTP/1.0\r\nHost: %s\r\n\r\n",
            path, data, reg, mac, devid, nonce, host);

#ifdef _WIN32						// Windows 10 case
    WSADATA wsa;
    SOCKET s;

    if (prt) printf("\nInitialising Winsock...");
    if (WSAStartup(MAKEWORD(2,2),&wsa) != 0)
    {
        printf("Failed. Error Code : %d",WSAGetLastError());
        return (char *) "-1";
    }

    if (prt) printf("Initialised.\n");

							//Create a socket
    if((s = socket(AF_INET , SOCK_STREAM , 0 )) == INVALID_SOCKET)
    {
        printf("Could not create socket : %d" , WSAGetLastError());
    }

    if (prt) printf("Socket created.\n");

    server = gethostbyname(host);
    serv_addr.sin_addr.s_addr = inet_addr(server->h_addr);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(portno);
    memset(&serv_addr,0,sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(portno);
    memcpy(&serv_addr.sin_addr.s_addr,server->h_addr,server->h_length);
							//Connect to remote server
    if (connect(s , (struct sockaddr *)&serv_addr , sizeof(serv_addr)) < 0)
    {
        printf("connect failed with error code : %d" , WSAGetLastError());
        return (char*) "-1";
    }

    if (prt) puts("Connected");
    if( send(s , message , (int) strlen(message) , 0) < 0)
    {
        printf("Send failed with error code : %d" , WSAGetLastError());
        return (char *) "-1";
    }
    if (prt) puts("Data Send\n");

							//Receive a reply from the server
    if((received = recv(s , response , 2000 , 0)) == SOCKET_ERROR)
    {
        printf("recv failed with error code : %d" , WSAGetLastError());
    }

    if (prt) puts("Reply received\n");

							//Add a NULL terminating character to make it a proper string before printing
    memcpy(output, response, received);
    output[received] = '\0';
    if (prt) puts(output);

    closesocket(s);
    WSACleanup();
#endif

#ifdef __linux__ 					// case of LINUX (Ubuntu/ARM32/ARM64)
    int bytes, sent;
    int sockfd;
    int total = strlen(message);
    //printf("MSGLEN: %d\n", total);
        						/* lookup the ip address */
    server = gethostbyname(host);
    if (server == NULL) error("ERROR, no such host");
        						/* create the socket */
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd < 0) error("ERROR opening socket");
        						/* fill in the structure */
        memset(&serv_addr,0,sizeof(serv_addr));
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(portno);
        memcpy(&serv_addr.sin_addr.s_addr,server->h_addr,server->h_length);
                					/* connect the socket */
        if (connect(sockfd,(struct sockaddr *)&serv_addr,sizeof(serv_addr)) < 0)
            error("ERROR connecting");
                					/* send the request */

    sent = 0;
    do {
        bytes = write(sockfd,message+sent,total-sent);
        if (bytes < 0)
            error("ERROR writing message to socket");
        if (bytes == 0)
            break;
        sent+=bytes;
    } while (sent < total);
    							/* receive the response */
    memset(response, 0, sizeof(response));
    total = sizeof(response)-1;
    received = 0;
    if (prt) printf("Response: \n");
    do {
       if (prt) printf("%s", response);
       memset(response, 0, sizeof(response));
       bytes = recv(sockfd, response, 1024, 0);
        if (bytes < 0)
           printf("ERROR reading response from socket");
       if (bytes == 0)
           break;
       received+=bytes;
       strcat(output, response);
    } while (1);

    if (received == total)
        error("ERROR storing complete response from socket");

    							/* close the socket */
    close(sockfd);
#endif


    free(message);

    return (output);
}

// ======================================== main program ============================================== //

//
// ======================================== vali-avx ============================================================================== //
//
								// global area
IGC_Key Key;							// the instance containing the PK data

SHA256 HashCalc;						// the instance containing the HASH SHA256 data

const int HashLen = 32;                                     	// Hash of the message
uint8_t Hash[HashLen]; 						// HASH output

//
// This porgram validates an .IGC file using the disgital signature stored on the las 2 records
//

int main(int argc, char *argv[])				// the argument is the File Name

{

#ifdef __linux__
  const char *pgmver=" Linux V1.0";				// program version
#elif  _WIN32
  const char *pgmver=" WIN   V1.0";				// program version
#endif
  int prt = 0;							// prinnt on|off
  printf("Program %s Version: %s %s %s\n", __FILE__, pgmver,  __DATE__, __TIME__);
  printf("Ver MBEDTLS: %s\n\n", MBEDTLS_VERSION_STRING_FULL);	// report the library version of the MBEDTLS library

  int msglen = 0;						// size of the file
  int buflen = 1024;						// working buffer in order to get the registration data
  char * response, *Message, *Temp, *buf;			// the response from the RegDB
  if (argc <= 1)
     {
     printf("An IGC file name is needed !!!! ...\n\n");
     exit(-1);
     }
  char* filename = argv[1];					// name of the file
  msglen=findSize(filename);					// find the file size in order to get the memory

  printf ("IGC File name: %s  File size: %d bytes\n", filename, msglen);
                      						// allocate and clean the working areas
  Message = (char *) malloc(msglen); 				// allocate the memory for reading the file
  Temp    = (char *) malloc(msglen); 				// the aux memory
  buf     = (char *) malloc(buflen); 				// the buffer to get the registration data
  memset(Message, 0, msglen);					// clean the areas
  memset(Temp,    0, msglen);
  memset(buf,     0, buflen);

  FILE *fd0 =fopen(filename, "r");				// we open as readonly
  if (!fd0)
      {
      printf("Invalid file: %s \n\n ", argv[1]); 		// report the error and exit
      exit(-1);
      }
  size_t l = fread( Message, 1, msglen,  fd0);			// read the file
  int mlen= (int) strlen(Message);				// check the size, it should be the same than msglen
  fclose(fd0);							// close as read file

								// now looks for the first G record
  l = 0;
  int first =  (int) l;
  int loopidx = mlen;
  while (loopidx > 0)						// find the 2 last G records
     {
     if (Message[loopidx] == 'G' && Message[loopidx -1] == '\n')
        {
        if (first != 0)						// if we found the first one (really the last)
           break;
        else
           first = loopidx;					// remember where it was
        }
     loopidx -= 1;						// keep scanning
     }
  if (loopidx == 0)
     {
      printf("Invalid format on file: %s \n\n ", argv[1]); 	// report the error and exit
      exit(-2);
      }
     
  char ghash[256];						// container for the HASH G record
  char gsign[256];						// container for the G siganture record
  memset(ghash, 0, sizeof(ghash));				// init to zeroes
  memset(gsign, 0, sizeof(gsign));
  memcpy(ghash, Message+loopidx, first - loopidx);		// copy the G hash record
  memcpy(gsign, Message+first, mlen - first);			// copy the G signature record
  *(gsign+mlen-first-1) = '\0';					// subtitute the NL for the string end
  *(gsign+mlen-first)   = '\0';					// subtitute the NL for the string end
#ifdef _WIN32
  *(strchr(gsign, '\n'))= '\0';					// in windows clean the NL
#endif
  for (int i=mlen-first; i < (int) sizeof(gsign); i++)
       *(gsign+i)='\0';
  if (strlen(gsign) != 143)
     {
     printf ("\n>>> Warning check the digital signature result .... wrong length detected !!! <<<\n");
     }
  printf("G records: Length %d %d\nMD  %s\nSIG %s\n", (unsigned int) strlen(ghash), (unsigned int) strlen(gsign), ghash, gsign);
  memcpy(Temp, Message, loopidx);				// copy up to the first G record to the temp  in order to compute the HASH value
  int Templen= (int) strlen(Temp);
  if (prt) printf("\nWorking areas\n%s%d\n", Temp, (int) strlen(Temp));
  
  HashCalc.Init();						// compute the HASH value
  HashCalc.Start();
  HashCalc.Update((const uint8_t *)Temp, strlen(Temp));
  HashCalc.Finish(Hash);					// on Hash area we have the HASH value in binary
  HashCalc.Free();

  char hexgrec[256];						// container for the HEX value of the HASH
  memset(hexgrec, 0, sizeof(ghash));				// clean it
  if (prt) printf("Hash[%d] \n", HashLen);
  for(int Idx=0; Idx<HashLen; Idx++)				// convert the HASH to hex
  { 
     if (prt) printf("%02X", Hash[Idx]); 
     sprintf(hexgrec+Idx*2,   "%02X", Hash[Idx]); 
  }
  //printf("\n"); //printf("%s", grec); //printf("\n"); //printf("%s", ghash);

  if (memcmp(hexgrec, ghash+1, strlen(hexgrec)) == 0)		// compare the HASH value just computed with the one form the file and chach if it is the same
     printf ("\nMessage Digest OK ...\n");
  else
     {
     printf ("\nNot matching HASH G record ...\n");
     exit(-1);
     }
// ================= get the data form registration database (MAC, REGIS; devid, and Publi Key) ==================== //
  								// Get the data from the registration DB 
  char * REGONFILE   = strstr(Temp, "HFGIDGliderID:")+14;	// the registration
  if (REGONFILE == NULL)
     {
     printf ("\nNot GliderID header found ...\n");
     exit(-1);
     }
  char * MACONFILE   = strstr(Temp, "LOGN")+36;			// the MAC addr
  if (MACONFILE == NULL)
     {
     printf ("\nNot MAC L record found ...\n");
     exit(-1);
     }

  char   regonfile[16];						// the reg
  char maconfile[16];						// the maca
  memset(regonfile, 0, sizeof(regonfile));			// clear it
  memset(maconfile, 0, sizeof(maconfile));			// clear it
  int reglen = (int) (strchr(REGONFILE, '\n') - REGONFILE);
  int maclen = (int) (strchr(MACONFILE, '\n') - MACONFILE);
  if (reglen  == 0 || maclen == 0)
     {
     printf ("\nRegistration or MAC not found one the headers ...\n");
     exit(-1);
     }

  memcpy(regonfile,(const void *) REGONFILE, strchr(REGONFILE, '\n') - REGONFILE);
  memcpy(maconfile,(const void *) MACONFILE, strchr(MACONFILE, '\n') - MACONFILE);
  
  response = getregdata(buf, buflen, regonfile, maconfile, prt);	// get the registration data

  if (prt) printf("Response: %d\n=========================\n%s\n========================\n", (int) strlen(response), response);
  if (strstr(response, "invalid token") != NULL)
     {
     printf("\n>>>> Invalid token <<<<\n");
     exit(-1);
     }

  char * json   = strstr(response, "{\"registration");		// we looks for this text
  if (json == NULL)
     {
     printf("\n>>>> Invalid REGISTRATION <<<<\n");		// if not found ... wrong data
     exit(-1);
     }
								// parse the JSON response
								// get the main key elements 
  char * MAC    = strstr(json, "reg_MAC")+11;
  char * REG    = strstr(json, "reg_registration")+20;
  char * DEVID  = strstr(json, "reg_devid")+13;
  char * PUBKEY = strstr(json, "reg_PublicKey")+17;
  *(MAC+16)             =0;
  *(strchr(REG,    '"'))=0;
  *(strchr(DEVID,  '"'))=0;
  *(strchr(PUBKEY, '"'))=0;
								// for testing very that the signature of the file is conformed !!! 
  unsigned char sigbin[256];					// the signature converted to binary
  unsigned char pubkey[1024];					// the extracted public key
                                 
  memset(pubkey, 0, sizeof(pubkey));				// eliminate the \r for the input
  for (int i=0, j=0; i< (int) sizeof(pubkey);i++, j++)
      {
      if (*(PUBKEY+i) == 0)
         break;
      if (*(PUBKEY+i) == '\\' && *(PUBKEY+i+1) == 'r')
          i +=3,  pubkey[j] = '\n';				// conver it to binary NEWLINE
      else
          pubkey[j] = *(PUBKEY+i);
      }

  if (prt) printf ("\nPublic Key: KL %zd SL%zd\nPK %s \n", (size_t) strlen((char *)pubkey), (size_t) strlen((char *) PUBKEY), pubkey); 

  int Res=0;							// response code
  Res = Key.Parse_PublicKey(pubkey, (int) strlen(PUBKEY)+1);	// set the KEY instance with the public key
  printf("Parse Public Key result: %s \n", Res ? "NOT OK ..." : "OK");	// report the result (valid or no valid)
  memset(sigbin, 0, sizeof(sigbin));				// initialize the container for the signature in binary
  hextobin(gsign+1, sigbin, sizeof(sigbin));			// convert to binary (we aware that can containe nulls in between
  for (int i=0; i < 256;i++)					//
      {
      if (prt) printf("%2.2d ",i);				// the index
      if (prt) printf("%X ", sigbin[i]);			// convert to hex
      }								
  Res=Key.Verify(sigbin, 71, (unsigned char *)Temp, Templen);	// verify the signature
  printf("Signature result: RC=%X %s\n", Res, Res ? "NOT OK ..." : "OK");	// report the result
  if (Res != 0)							// if error report it from the mbedtls routines messages
      {
      char mbedtlserror[128];
      mbedtls_strerror(Res, mbedtlserror, 128);
      printf ("MBEDTLS error: %s \n\n", mbedtlserror);
      }
  free(response);						// release the working areas
  free(Message);						// release the working areas
  free(Temp);							// release the working areas
  return Res; 
}

