var os = navigator.platform;
var browser = navigator.appName;
var prod = navigator.product;
var browserver =  navigator.appVersion;

if(os == 'Linux x86_64' && browser == 'Netscape' && prod == 'Gecko' )
{
  var skip = '1';
  alert(browserver)
}else{
  alert([browserver,'Browsing files only works from the cluster login node!'])
}
