# P2P-Network
this is an implementation of a P2P Network
peer: 

  1- can send document or image to other peers
  
  2- talk with server
  
    2.1- ask for list of all user-ids
    
    2.2- ask for address of a peer
    
    2.3- register with server
    
server:

  provides the facility to familiarize peers with each other.
  
redis:

  holds key-value pairs with format <user-id, address>
  
address:

  = IPv4 + ":" + port
