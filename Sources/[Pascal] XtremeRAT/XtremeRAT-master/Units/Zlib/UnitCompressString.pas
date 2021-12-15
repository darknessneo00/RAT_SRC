unit UnitCompressString;

interface

uses
  windows;

function CompressString(str: widestring): widestring;
function DeCompressString(str: widestring): widestring;

implementation

uses
  ZLibEx,
  StreamUnit;

function IntToStr(i: Int64): widestring;
begin
  Str(i, Result);
end;

function StrToInt(S: widestring): Int64;
var
  E: integer;
begin
  Val(S, Result, E);
end;

function CompressString(str: widestring): widestring;
var
  oCompress               : TZCompressionStream;
  inpStream, outStream    : TMemoryStream;
begin
  inpStream := TMemoryStream.Create;
  outStream := TMemoryStream.Create;

  StrToStream(inpStream, str);
  inpStream.Position := 0;
                                                     //zcNone, zcFastest, zcDefault, zcMax
  oCompress := TZCompressionStream.Create(outStream, zcFastest);
  oCompress.CopyFrom(inpStream, inpStream.Size);
  oCompress.Free;

  result := StreamToStr(outStream);

  inpStream.Free;
  outStream.Free;
end;


function DeCompressString(str: widestring): widestring;
const
  BufferSize = 4096;
var
 oDecompress             : TZDecompressionStream;
 inpStream               : TMemoryStream;
 outStream               : TMemoryStream;
 Buffer                  : array[0..BufferSize-1] of Byte;
 Count                   : integer;
begin
  result := '';

  inpStream := TMemoryStream.Create;
  outStream := TMemoryStream.Create;

  StrToStream(inpStream, str);
  inpStream.Position := 0;

  oDecompress := TZDecompressionStream.Create(inpStream);

  while True do
  begin
    Count := oDecompress.Read(Buffer, BufferSize);
    if Count <> 0 then outStream.WriteBuffer(Buffer, Count) else Break;
  end;
  oDecompress.Free;

  result := StreamToStr(outStream);

  inpStream.Free;
  outStream.Free;
end;

end.
