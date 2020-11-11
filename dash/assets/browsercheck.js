var os = navigator.platform;
var browser = navigator.appName;
var prod = navigator.product;
var browserver =  navigator.appVersion;

if(os == 'Linux x86_64' && browser == 'Netscape' && prod == 'Gecko' && browserver =='5.0 (X11)' )
{
  var skip = '1';

}else{
  alert(['Browsing files only works from the cluster login node!'])
}
