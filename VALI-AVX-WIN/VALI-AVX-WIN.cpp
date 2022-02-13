// VALI-AVX-WIN.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
//#pragma warning(suppress : 4996)

#include <iostream>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/types.h>

#include "vali-avx.h"

IGC_Key Key, Key2;

SHA256 HashCalc;

static uint8_t Data[10 * 1024];                                  // temporary Data to train write/read
// static char Output[1024];

//const char *Message = "Test message for OGN-Tracker crypto-signature - make it a bit longer for SHA512"; // Message to Hash and sign
const int HashLen = 32;                                     // Hash of the message
uint8_t Hash[HashLen]; // = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F };



int main(int argc, char* argv[])

{
    int msglen = 100 * 1024;
    char* Message = (char*)malloc(msglen);
    printf("IGC File: %s\n", argv[1]);				// name of the file
    FILE * *fd0;
    fopen_s(fd0,argv[1], "rb");				// initially we open as readonly
    if (!fd0)
    {
        printf("Invalid file: %s \n\n ", argv[1]);
        exit(-1);
    }
    int len = fread(Message, msglen, 1, *fd0);			// read the file
    printf("Msglen: %d %d\n", len, (int)strlen(Message));	// the message is the whole file
    fclose(*fd0);							// close as read file
  //       Now open the file as append in order to add the 2 "G" records (hash and signature)
    
    fopen_s(fd9, argv[1], "a");					// open now as write file
    HashCalc.Init();
    HashCalc.Start();
    HashCalc.Update((const uint8_t*)Message, strlen(Message));
    HashCalc.Finish(Hash);
    HashCalc.Free();

    printf("Ver MBEDTLS: %s\n\n", MBEDTLS_VERSION_STRING_FULL);

    printf("Message[%d] %s\n", (int)strlen(Message), Message);
    printf("Hash[%d] ", HashLen);

    fputc('G', *fd0);						// place the hash value as the 1st G record
    for (int Idx = 0; Idx < HashLen; Idx++)
    {
        printf("%02X", Hash[Idx]);
        fprintf(fd0, "%02X", Hash[Idx]);
    }
    printf("\n");
    fputc('\n', fd0);

    int Ret = Key.Init();
    printf("Key.Init() => %d\n", Ret);

    Ret = Key.Generate();						// generate the ECC keys (private and public)
    printf("Key.Generate() => %d\n", Ret);
    // printf("sizeof(Key-Pair) = %d+%d+%d\n", sizeof(SignCtx.grp), sizeof(SignCtx.d), sizeof(SignCtx.Q));

    int Len = Key.Pub_WriteBin(Data, 2048);				// get the public key
    printf("Key.Pub_WriteBin() => %d\n", Len);
    for (int Idx = 0; Idx < Len; Idx++)
    {
        printf("%02X", Data[Idx]);
    }
    printf("\n");

    Len = Key.Priv_WriteBin(Data, 72);				// get the private key
    printf("Key.PrivWriteBin() => %d\n", Len);
    for (int Idx = 0; Idx < 72; Idx++)
    {
        printf("%02X", Data[Idx]);
    }
    printf("\n");

    memset(Data, 0, sizeof(Data));
    Len = Key.Pub_Write(Data, 2048);				// get the public key in PEM format
    printf("Key.Pub_Write() => %d\n", Len);
    printf("%s", Data);
    FILE* fd1 = fopen("pubkey.PEM", "wb");				// and write it to a file for testing
    fprintf(fd1, "%s", Data);
    fclose(fd1);
    memset(Data, 0, sizeof(Data));
    Len = Key.Priv_Write(Data, 2048);				// get the private key in PEM format
    printf("Key.Priv_Write() => %d\n", Len);
    printf("%s", Data);
    FILE* fd2 = fopen("prikey.PEM", "wb");				// and write it on a file for testing
    fprintf(fd2, "%s", Data);
    fclose(fd2);

    memset(Data, 0, sizeof(Data));
    Len = Key.Pub_Write_DER(Data, 2048);				// now in DER format
    printf("Key.Pub_Write_DER() => %d\n", Len);
    printf("%s", Data);
    FILE* fd3 = fopen("pubkey.DER", "wb");
    for (int Idx = 0; Idx < Len; Idx++)
    {
        fputc(Data[Idx], fd3);
    }
    fclose(fd3);
    memset(Data, 0, sizeof(Data));
    Len = Key.Priv_Write_DER(Data, 2048);				// now in DER format
    printf("Key.Priv_Write_DER() => %d\n", Len);
    printf("%s", Data);
    FILE* fd4 = fopen("prikey.DER", "wb");
    for (int Idx = 0; Idx < Len; Idx++)
    {
        fputc(Data[Idx], fd4);
    }
    fclose(fd4);

    Len = Key.Write(Data);
    printf("Key.Write() => %d\n", Len);

    //
    // ================= SIGN the message disgest =======================
    //
    FILE* fd5 = fopen("tracker.sign", "wb");			// file in hex
    FILE* fd6 = fopen("tracker.sign.bin", "wb");			// file signature in binary for testing purposes

  // the second "G" record contains the DSA signature of the file
    fputc('G', fd0);						// place the digital signature as the 2nd. G record

    Len = Key.Sign_MD5_SHA256(Data, Hash, HashLen);
    printf("Key.Sign_SHA256() => %d\n", Len);
    for (int Idx = 0; Idx < Len; Idx++)
    {
        printf("%02X", Data[Idx]);
        fputc(Data[Idx], fd6);
        fprintf(fd5, "%02X", Data[Idx]);
        fprintf(fd0, "%02X", Data[Idx]);
    }
    printf("\n");
    fputc('\n', fd0);
    fclose(fd5);							// close the hex signature file
    fclose(fd6);							// close the binary signature file
    fclose(fd0);							// close the modified IGC file with the 2 "G" records

   // for testing very that the signature of the file is conformed !!! 
    unsigned char sig[sizeof(Data)];
    memcpy(sig, Data, sizeof(Data));
    //  int Verify_SHA256(unsigned char *Sign, int sig_len, const uint8_t *Hash, int HashLen)      // Verify a signature
    int Res = Key.Verify_SHA256(sig, Len, Hash, HashLen);		// verify the signature
    printf("Sign result: %d\n\n", Res);


    return 0;
}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
