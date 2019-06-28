/*
MIT License

Copyright (c) 2019 limusina10

Permission is hereby granted, free of charge, to any person obtaining a copy of tShis software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*///ESTE CODIGO NO AFECTARA SU BOT, SCRIPT DE ARRANQUE

const http = require('http');
const express = require('express');
const app = express();

app.use(express.static('public'));

app.get("/", function (request, response) {
    response.sendFile(__dirname + '/views/index.html');
});

app.get("/", (request, response) => {
    response.sendStatus(200);
});

app.listen(process.env.PORT);

setInterval(() => {
    http.get(`http://${process.env.PROJECT_DOMAIN}.glitch.me/`); 
}, 280000);


//DESDE AQUI EMPIEZA A ESCRIBIR EL CODIGO PARA SU BOT

const Discord = require("discord.js");
const client = new Discord.Client();
const config = require("./config.json");
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database("./mybotdata.sqlite");

client.on("ready", () => {
    var date = new Date();
     console.log("Estoy listo! " + date);
    /*let estado = ['Use .help',`Active on ${client.guilds.size} guilds`,'Dev: limusina10#6341']
    let random = Math.floor((Math.random() * estado.length))
    let estado2 = estado[random];*/
    client.user.setPresence( {

        game: {
            name: `Use /help | Active with ${client.users.size} users `,
            type: "PLAYING"
        }
    })
    }, //4000  //cada cuanto cambia
    );
//add members
client.on("guildMemberAdd", (member) => {
    var id = member.guild.id
    //start search if the channel was configurated before
    let join = `SELECT * FROM log WHERE idguild = ${id}`;
    db.get(join, (err, filas) => {
       if (err) return console.error(err.message)
        if (filas){
            let databasechnl = `${filas.channelid}`;
            let canal = client.channels.get(`${databasechnl}`); 
            const embed = new Discord.RichEmbed()
             .setThumbnail(member.user.avatarURL)
             .setColor(0x0E83A)
             .setAuthor(`${member.user.username} has joined the server`, member.user.avatarURL)
             .setDescription(`Welcome ${member.user.username}#${member.user.discriminator} to ${member.guild.name}`)
             .setTimestamp()
             .setFooter("Have fun in our server!")
            canal.send({embed});
        } else {

        }
    });
    });
///left memebers
client.on("guildMemberRemove", (member) => {
    var id = member.guild.id
    //start search if the channel was configurated before
    let join = `SELECT * FROM log WHERE idguild = ${id}`;
    db.get(join, (err, filas) => {
       if (err) return console.error(err.message)
        if (filas){
            let databasechnl = `${filas.channelid}`;
            let canal = client.channels.get(`${databasechnl}`); 
            const embed = new Discord.RichEmbed()
             .setThumbnail(member.user.avatarURL)
             .setColor(0Xff0000)
             .setAuthor(`${member.user.username} has left the server`, member.user.avatarURL)
             .setDescription(`Bye! ${member.user.username}#${member.user.discriminator}`)
             .setTimestamp()
             .setFooter("See you soon!")
            canal.send({embed});
        } else {

        }
    });
    
});
client.on("messageDelete", (message) => {
    var id = member.guild.id
    //start search if the channel was configurated before
    let rm = `SELECT * FROM log WHERE idguild = ${id}`;
    db.get(rm, (err, filas) => {
       if (err) return console.error(err.message)
        if (filas){
            let dbcnhlid = `${filas.channelid}`;
            let canal = client.channels.get(`${dbcnhlid}`);
            const embed = new Discord.RichEmbed()
            .setColor(0xbc1b0d)
            .setAuthor("Message Deleted")
            .addField('User:',`${message.author.username}`)
            .addField('Mensaje Message:',`${message}`)
            .setTimestamp()
            canal.send({embed});
        } else {

        }
    });
});
/*MODO EDICIÓN EN PRACTICAS ------------------------------------------
client.on('messageUpdate', (oldMessage, newMessage) => {
     if (oldMessage.guild.id == "528741398292332554") {
    let canal = client.channels.get('538233514047569932'); 
    const embed = new Discord.RichEmbed()
    .setColor(0xbc1b0d)
    .setAuthor("Mensaje editado")
    .addField('Mensaje Antiguo:',``)
    .addField('Mensaje Nuevo:',``)
    .setTimestamp()
    canal.send({embed});
     }
}); // -------------------------------------------------------------*/


//check if is not DM
var prefix = config.prefix;
client.on("message", (message) => {
    //error developer / owner
    const DevEmbed = new Discord.RichEmbed() 
    .setColor(0xbc1b0d)
    .setAuthor(`Hammer Error`, client.user.avatarURL)
    .setThumbnail(client.user.avatarURL)
    .setDescription(":no_entry: `Error` :no_entry: `|` You aren't the owner.")
    .setFooter("ERROR #001")
    .setTimestamp;

    //error args
    const ArgsEmbed = new Discord.RichEmbed() 
    .setColor(0xbc1b0d)
    .setAuthor(`Hammer Error`, client.user.avatarURL)
    .setThumbnail(client.user.avatarURL)
    .setDescription(":no_entry: `Error` :no_entry: `|` You didn't write the required args.")
    .setFooter("ERROR #002")
    .setTimestamp;

    //administator perms
    const AdminPerms = new Discord.RichEmbed() 
    .setColor(0xbc1b0d)
    .setAuthor(`Hammer Error`, client.user.avatarURL)
    .setThumbnail(client.user.avatarURL)
    .setDescription(":no_entry: `Error` :no_entry: `|` You haven't a special permission.")
    .setFooter("ERROR #003")
    .setTimestamp;

    

    if(message.channel.type == "dm") return;
    //commands -----------------------------------------------------
    if (message.content.startsWith(prefix + "hello")) {
    message.reply("``Hello World``");
    }
    if (message.content.startsWith(prefix + "help")) {
        let user = message.author;

        const embed = new Discord.RichEmbed()
        .setColor(0x0E83A)
        .setAuthor(`Hammer Help`, client.user.avatarURL)
        .setThumbnail(client.user.avatarURL)
        .addField('**Prefix:**', "``/``")
        .addField("**Hammer's Team:**", "``limusina10#6341, GashohFDEZ#3722, Mariete05#4835``")
        .addField('**Status: **', "``Online, 99,7% uptime``")
        .addField('**Moderator Commands:**', "``warn, uwnarn, topwarns, kick, ban, addrole, removerole, createrole, lock, unlock``")
        .addField('**Automod:**', '``Blocks about 100 swear words``')
        .addField('**Info Commands:**', "``help, hammer, ping, hello, assistance, whois, guild, roles``")
        .addField('**Bot Customizing:**', "``log``")
        .addField('**Invite:**', ":link:[Click Here](https://discordapp.com/api/oauth2/authorize?client_id=591633652493058068&permissions=8&scope=bot)")
        .setTimestamp()
        .setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
        user.send({embed});

        message.reply(":white_check_mark: Check your Direct Messages! :envelope:");
    }
  
    if (message.content.startsWith(prefix + "eval")) {
        if(message.author.id !== config.idOwner) return message.channel.send(":no_entry: `Error` :no_entry: `|` You aren't the owner.");
        const args = message.content.split(" ").slice(1);
        
        function clean(text) {
        if (typeof(text) === "string")
            return text.replace(/`/g, "`" + String.fromCharCode(8203)).replace(/@/g, "@" + String.fromCharCode(8203));
            else
            return text;
        }
        try {
            const code = args.join(" ");
            let evaled = eval(code);
        
        if (typeof evaled !== "string")
            evaled = require("util").inspect(evaled);
        
            message.channel.send(clean(evaled), {code:"xl"});
        } catch (err) {
        message.channel.send(`\`ERROR\` \`\`\`xl\n${clean(err)}\n\`\`\``);
    }

    }
    /*if (message.content.startsWith(prefix + "")) {
    message.channel.send(":no_entry: `Error` :no_entry: `|` You didn't write the command, only yhe prefix.");
    }*/
    if (message.content.startsWith(prefix + "stats")) {
    const moment = require("moment");
     require('moment-duration-format');

    const actividad = moment.duration(client.uptime).format(" D [days], H [hrs], m [mins], s [secs]");
    let ping = Math.floor(message.client.ping);

    const embed = new Discord.RichEmbed()
     .setColor(0x0E83A)
     .setAuthor(`Stats info`, client.user.avatarURL)
     .addField(`**Owner/Developer**`, "`limusina10#6341`", true)
     .addField(`**Version**`, `3.1.4`, true)
     .addField(`**Library**`, `Discord ^11.2.1 (Js)`, true)

     .addField(`**Memory**`, `${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB`, true)
     .addField(`**Uptime**`, `${actividad}`, true)
     .addField(`**Servers**`, `${client.guilds.size.toLocaleString()}`, true)

     .addField(`**Users**`, `${client.users.size.toLocaleString()}`, true)
     .addField(`**Channels**`, `${client.channels.size.toLocaleString()}`, true)
     .addField(`**Ping**`, `${ping} ms`, true)

    message.channel.send({embed});

    }
    if (message.content.startsWith(prefix + "warn")) {
        var perms = message.member.hasPermission("ADMINISTRATOR");
        if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You haven't the ADMINISTRATOR permssion.");
        const args = message.content.split(" ").slice(1);
        var user = message.author
        var server = message.guild;
        var warned = message.mentions.users.first();
        var razon = args.slice(1).join(' ');
        
        if (message.mentions.users.size < 1) return message.reply('Who?.').catch(console.error);
        if(!razon) return message.channel.send('Write a reason, `.warn @username [reason]`');
        
        const embed = new Discord.RichEmbed()
        .setAuthor("User Warned", client.user.avatarURL)
        .addField("Moderator: ", user)
        .addField("User Warned: ", warned)
        .addField("Reason: ", razon)
        .setDescription("Be carefully, at the 3 warns you will be muted or kicked by Hammer BOT ")
        .setColor(0Xff0000)
        .setTimestamp()
        
        message.channel.send({embed});
        warned.send({embed});

        let SQL = "CREATE TABLE IF NOT EXISTS usuarios (idusuario TEXT, warns INTEGER)";

        db.run(SQL, function(err) {
            if (err) return console.error(err.message)
        })
        //insert if not exists user in db
        // Agregar debajo del comentario: <-- INSERT USUARIO -->

        let id = warned.id;
        let sentencia = `SELECT * FROM usuarios WHERE idusuario = ${id}`;

        db.get(sentencia, (err, filas) => {
            if (err) return console.error(err.message)

            if (!filas){

                //was warned before
              let insert = `INSERT INTO usuarios(idusuario, warns) VALUES(${id}, 1)`;

              db.run(insert, function(err) {
               if (err) return console.error(err.message)
              });

            } else {
                //was never warned before
               let update = `UPDATE usuarios SET warns = ${filas.warns + 1} WHERE idusuario = ${id}`;
                db.run(update, function(err) {
                       if (err) return console.error(err.message)
                      });
            }


        });
        let getnumofwaarnsindb = `SELECT * FROM usuarios WHERE idusuario = ${id}`;
        db.get(getnumofwaarnsindb, (err, filas) => {
            if (err) return console.error(err.message)
            
            if (filas){
                
                //user registered and warned before+
                let numofwarns = `${filas.warns}`
                if (numofwarns > 2) {
                    let user = filas.idusuario
                    let razon = "Too many warns"

                    var admin = "Hammer Bot";
                    var server = message.guild;
                    
                    var banned = user

                    if (!message.guild.member(banned).kickable) return message.reply("I can't kick this member. Please use /unwarn to that user.");
                
                    let update = `UPDATE usuarios SET warns=0 WHERE idusuario = ${user}`;

                    db.run(update, function(err) {
                        if (err) return console.error(err.message)
                    });

                    message.guild.member(banned).kick(razon);
                    let name = client.users.get(banned).tag
                    message.channel.send(`The user **${name}** has been kicked because had too many warns.`);
                } else {
                    //has no 3 warns
                }
            } else {
              //User not registered in db
            }

        });
    

      
    }


    
  if (message.content.startsWith(prefix + "kick")) {
    const args = message.content.slice(prefix.length).trim().split(/ +/g);
    const command = args.shift().toLowerCase();
    let user = message.mentions.users.first()
    || client.users.get(args[0]) 
    || client.users.find(x => x.tag === args.join(" "))
    let razon = args.slice(1).join(' ');

    var perms = message.member.hasPermission("KICK_MEMBERS");

    if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You don't have KICK_MEMBERS permssion.");
    if (message.mentions.users.size < 1) return message.reply('Who?').catch(console.error);
    message.delete(100);
    if (!razon) return message.channel.send('Write a reason, `/kick @username [reason]`');
    if (!message.guild.member(user).kickable) return message.reply("I can't kick this member.");
     
    message.guild.member(user).kick(razon);
    

    var admin = message.author
    var server = message.guild;
    
    var banned = message.mentions.users.first();

    const embed = new Discord.RichEmbed()
    .setAuthor("User Kicked", client.user.avatarURL)
    .addField("Moderator: ", admin)
    .addField("User Kicked: ", banned)
    .addField("Reason: ", razon)
    .setColor(0Xff0000)
    .setTimestamp()
    
    message.channel.send({embed});
    banned.send({embed});
  }

  if (message.content.startsWith(prefix + "addrole")) {
    const args = message.content.slice(prefix.length).trim().split(/ +/g);
    const command = args.shift().toLowerCase();
    let miembro = message.mentions.members.first();
    let nombrerol = args.slice(1).join(' ');

    let role = message.guild.roles.find("name", nombrerol);
    let perms = message.member.hasPermission("MANAGE_ROLES_OR_PERMISSIONS");

    if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You don't have MANAGE_ROLES_OR_PERMISSIONS permssion.");
     
    if(message.mentions.users.size < 1) return message.reply('Who?').catch(console.error);
    if(!nombrerol) return message.channel.send('Write the name of the role to add,`.addrol @member [Role]`');
    if(!role) return message.channel.send('Role not found on this server.');
    
    miembro.addRole(role).catch(console.error);
    message.channel.send(`The role **${role.name}** was succesfully added to **${miembro.user.username}**.`);
  }
  if (message.content.startsWith(prefix + "removerole")) {
    const args = message.content.slice(prefix.length).trim().split(/ +/g);
    const command = args.shift().toLowerCase();
    let miembro = message.mentions.members.first();
    let nombrerol = args.slice(1).join(' ');

    let role = message.guild.roles.find("name", nombrerol);
    let perms = message.member.hasPermission("MANAGE_ROLES_OR_PERMISSIONS");

    if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You don't have MANAGE_ROLES_OR_PERMISSIONS permssion.");
     
    if(message.mentions.users.size < 1) return message.reply('Who?').catch(console.error);
    if(!nombrerol) return message.channel.send('Write the name of the role to remove, `.removerol @member[Role]`');
    if(!role) return message.channel.send('Role not found on this server.');
    
    miembro.removeRole(role).catch(console.error);
    message.channel.send(`The role **${role.name}** of **${miembro.user.username}** was removed succesfully.`);
  }
  if (message.content.startsWith(prefix + "createrole")) {
    /*const embed = new Discord.RichEmbed()
    .setAuthor('Comming Soon...')
    .setThumbnail(client.user.avatarURL)
    .addField("You've found a...", 'Comming Soon command.')
    .addField("Type: ", '.help to get help')
    .setColor(0xff4d4d)
    message.channel.send({embed})*/
    var guild = message.guild;
    var perms = message.member.hasPermission("MANAGE_ROLES_OR_PERMISSIONS");
    
    if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You don't have MANAGE_ROLES_OR_PERMISSIONS permssion.");
    
    const args = message.content.slice(prefix.length).trim().split(/ +/g);
    const command = args.shift().toLowerCase();
    
    if(!args) return message.channel.send('Add a name of the role.');
    message.guild.createRole({
    name: args.join(" "),
    color: 'BLUE'
    }).then(role => {message.channel.send('New role created: '+role+'.')});
  }
    if (message.content.startsWith(prefix + "ping")) {
    let ping = Math.floor(message.client.ping);

    message.channel.send(":ping_pong: Pong!")
    .then(m => {
       const embed = new Discord.RichEmbed()
       .setDescription(`:incoming_envelope: Ping Messages: \`${m.createdTimestamp - message.createdTimestamp} ms\`\n:satellite_orbital: Ping DiscordAPI: \`${ping} ms\``)
       .setColor(0x00AE86)    
       m.edit({embed});
    })
  }
  if (message.content.startsWith(prefix + "db")) {
    if(message.author.id !== config.idOwner) return message.channel.send(":no_entry: `Error` :no_entry: `|` You aren't the owner.");
    //ALERT! ONE USE COMMAND!
    const sqlite3 = require('sqlite3').verbose();
    const db = new sqlite3.Database("./mybotdata.sqlite");
    let SQL = "CREATE TABLE IF NOT EXISTS usuarios (idusuario TEXT, warns INTEGER)";

    db.run(SQL, function(err) {
        if (err) return console.error(err.message)
    })
    message.channel.send("Succesfully DB");
    
  }
    ;
    const palabras  = ["Bugger", "Tosspot", "Scumsucker", "Scumbag", "Shithead", "Shitforbrains", "Wazzock", "Twit", "Twat", "Twot", "Twat Face", "Muppet", "Dipstick", "Moron", "Birdbrain", "Cuntchops", "Berk", "Arsehole", "Prat, Prannie", "Smeghead", "Ratbag", "Nonce", "Lunatic, Fag", "Faggot", "Nutter, Imbecile, Mong, Spack Head, Spacker, Cretin, Crouton or Spaz", "Dick Head", "Turd", "Bozo", "Bellend", "Bastard", "Prick, Dildo", "Berk", "Scallywag (tame and lame)", "Dolt", "Amoeba", "Fuckwit", "Fuckface", "Fathead", "Gimp", "Goon", "Clown", "Leg End", "Lump, Nitwit, Numpty: Noodle", "Dope", "Dunce", "Drongo", "Peabrain", "Runt", "Rascal or Rogue (twee)", "Sap", "Spunkbubble", "Tit", "Twerp", "Wally", "Weirdo", "Bollocks", "Git", "Gormless", "Knobhead", "Minger", "Pillock", "Plonker", "Ponce", "Prat", "Slag", "Slapper", "Twat", "Toff", "Wanker", "Cunt"];
    if(palabras.some(p => message.content.includes(p))){
         if(message.author.bot) return;
        //delete the bad word
        message.delete(100)
          

    
        var user = "Hammer Bot";
        var server = message.guild;
        var warned = message.author;
        var razon = "Typed a banned word in Hammer's Word Blacklist.";
        
        
       
      
        const embed = new Discord.RichEmbed()
        .setAuthor("User Warned", client.user.avatarURL)
        .addField("Moderator: ", user)
        .addField("User Warned: ", warned)
        .addField("Reason: ", razon)
        .setDescription("Be carefully, at the 3 warns you will be muted or kicked by a server moderator, ")
        .setColor(0Xff0000)
        .setTimestamp()
        
        message.channel.send({embed});
        warned.send({embed});


        //warns counts into db
        //connect to db
        
        let SQL = "CREATE TABLE IF NOT EXISTS usuarios (idusuario TEXT, warns INTEGER)";

        db.run(SQL, function(err) {
            if (err) return console.error(err.message)
        })
        //insert if not exists user in db
        // Agregar debajo del comentario: <-- INSERT USUARIO -->

        let id = message.author.id;
        let select = `SELECT idusuario, warns FROM usuarios WHERE idusuario = ${id}`;

        db.get(select, (err, filas) => {
            if (err) return console.error(err.message)
            if (!filas){

                //was warned before
              let insert = `INSERT INTO usuarios(idusuario, warns) VALUES(${id}, 1)`;

              db.run(insert, function(err) {
               if (err) return console.error(err.message)
              });

            } else {
                //was never warned before
               let update = `UPDATE usuarios SET warns = ${filas.warns + 1} WHERE idusuario = ${id}`;
                db.run(update, function(err) {
                       if (err) return console.error(err.message)
                      });
            }

        });
        //check if user has reached 3 warns to be able to kick him/her
        
        let sentenciados = `SELECT idusuario, warns FROM usuarios WHERE idusuario = ${id}`;
        db.get(sentenciados, (err, filas) => {
            if (err) return console.error(err.message)
            if (!filas){
                //User not registered in db
            } else {
              //user registered and warned before
                if (filas.warns >= 3) {
                    let user = filas.idusuario
                    let razon = "To many warns"

                    var admin = "Hammer Bot";
                    var server = message.guild;
                    
                    message.channel.send("/kick " + user + " "  + razon);
                } else {
                    //has no 3 warns
                }
            }

        });
    }
    if (message.content.startsWith(prefix + "hammer")) {
        const embed = new Discord.RichEmbed()
            .setThumbnail(client.user.avatarURL)
            .setColor(0x0E83A)
            .setAuthor(`Hammer Bot`, client.user.avatarURL)
            .setURL("https://discordapp.com/api/oauth2/authorize?client_id=591633652493058068&permissions=8&scope=bot")
            .setDescription(`A moderation Bot, wich has lots of funtional commands, from the basically (warn, kick or ban) to advanced functions like automod, with about 100 blocked swear words. Also is 99.7% uptime. **#DiscordHackWeek Creation** `)
            .setTimestamp()
            .setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
        message.channel.send({embed});
    }

     if (message.content.startsWith(prefix + "topwarns")) {
        var perms = message.member.hasPermission("KICK_MEMBERS");
        if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You don't have KICK_MEMBERS permssion.");
        //connect to db
        let lista = `SELECT idusuario, warns FROM usuarios ORDER BY warns DESC LIMIT 10`
        let embed = new Discord.RichEmbed()

        db.all(lista, (err, filas) => {
          if (err) return console.error(err.message)
          let datos = [];

          filas.map(ls => {
           if(client.users.get(ls.idusuario)){
            datos.push('__' + client.users.get(ls.idusuario).tag + '__, Warns: **'+ls.warns+'**')
           }
        
          });

          embed.setAuthor('Users List (TOP Warns)', client.user.avatarURL)
          embed.setDescription(datos.join('\n'))       
          embed.setColor(0Xff0000);
          embed.setTimestamp();
          embed.setThumbnail(client.user.avatarURL)
          embed.setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
        
          message.channel.send(embed);

         });
     }
    if (message.content.startsWith(prefix + "assistance")) {
        //connect to db
        let userm = message.mentions.users.first()

        if(!userm){
            //no @
            var user = message.author;
            
        

            let id = message.author.id;
            let sentencia = `SELECT idusuario, warns FROM usuarios WHERE idusuario = ${id}`;

            db.get(sentencia, (err, filas) => {
                if (err) return console.error(err.message)
                    
                        
                if (!filas){
                    //not exists
                    const embed = new Discord.RichEmbed()
                    .setThumbnail(message.author.avatarURL)
                    .setColor(0x0E83A)
                    .setAuthor(`Account Status of ${message.author.username}#${message.author.discriminator}`, message.author.avatarURL)
                    .setDescription(`Secure Level: (Nº of warns) 0 (You're a good member)`)
                    .setTimestamp()
                    .setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
                    message.channel.send({embed});
                } else {
                    let numwarns = `${filas.warns}` ;
                    console.log(numwarns);
                    //warned before
                    //if (numwarns = '0') {
                        //not exists
                        const embed = new Discord.RichEmbed()
                        .setThumbnail(message.author.avatarURL)
                        .setColor(0x28b7ff)
                        .setAuthor(`Account Status of ${message.author.username}#${message.author.discriminator}`, message.author.avatarURL)
                        .setDescription(`Secure Level: (Nº of warns): ** ${filas.warns}**. Be carefully, because at the 3 warns you will be kicked by Hammer BOT.`)
                        .setTimestamp()
                        .setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
                        message.channel.send({embed});
                    }
             

            });
        } else {
            let usrnmid = userm.id;
            let select = `SELECT idusuario, warns FROM usuarios WHERE idusuario = ${usrnmid}`;
             db.get(select, (err, filas) => {
                if (err) return console.error(err.message)
                    
                        
                if (!filas){
                    //not exists
                    const embed = new Discord.RichEmbed()
                    .setThumbnail(message.author.avatarURL)
                    .setColor(0x0E83A)
                    .setAuthor(`Account Status of ${userm.username}#${userm.discriminator}`, userm.avatarURL)
                    .setDescription(`Secure Level: (Nº of warns) 0 (You're a good member)`)
                    .setTimestamp()
                    .setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
                    message.channel.send({embed});
                } else {
                    let numwarns = `${filas.warns}` ;
                    console.log(numwarns);
                    //warned before
                    //if (numwarns = '0') {
                        //not exists
                        const embed = new Discord.RichEmbed()
                        .setThumbnail(message.author.avatarURL)
                        .setColor(0x28b7ff)
                        .setAuthor(`Account Status of ${message.author.username}#${message.author.discriminator}`, message.author.avatarURL)
                        .setDescription(`Secure Level: (Nº of warns): ** ${filas.warns}**. Be carefully, because at the 3 warns you will be kicked by Hammer BOT.`)
                        .setTimestamp()
                        .setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
                        message.channel.send({embed});
                }
            
            });

        }
    }

    
    if (message.content.startsWith(prefix + "ban")) {
        const args = message.content.slice(prefix.length).trim().split(/ +/g);
        const command = args.shift().toLowerCase();
        let user = message.mentions.users.first();
        let razon = args.slice(1).join(' ');
            
        var perms = message.member.hasPermission("BAN_MEMBERS");
        if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You don't have BAN_MEMBERS permssion.");
            
        if (message.mentions.users.size < 1) return message.reply('Who?.').catch(console.error);
        if(!razon) return message.channel.send('Write a reason, `/ban @username [reason]`');
        if (!message.guild.member(user).bannable) return message.reply("I can't ban this member.");
            
        
        message.guild.member(user).ban(razon);
        
        var admin = message.author
        var server = message.guild;
        
        

        const embed = new Discord.RichEmbed()
        .setAuthor("User Banned", client.user.avatarURL)
        .addField("Moderator: ", admin)
        .addField("User Banned: ", user)
        .addField("Reason: ", razon)
        .setColor(0Xff0000)
        .setTimestamp()
        
        message.channel.send({embed});
        user.send({embed});
  }
    if (message.content.startsWith(prefix + "unwarn")) {
        var perms = message.member.hasPermission("ADMINISTRATOR");
        const args = message.content.slice(prefix.length).trim().split(/ +/g);
        const command = args.shift().toLowerCase();
        let user = message.mentions.users.first();
        if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You don't have ADMINISTRATOR permssion.");
        let razon = args.slice(1).join(' ');
        if(!razon) return message.channel.send('Write a reason, `/unwarn @username [reason]`');

        if (message.mentions.users.size < 1) return message.reply('Who?.').catch(console.error);

        let id = user.id;
        let sql = `SELECT idusuario, warns FROM usuarios WHERE idusuario = ${id}`;

        db.get(sql, (err, filas) => {
            if (err) return console.error(err.message)
                
        if (!filas){
            message.channel.send(":no_entry: `Error` :no_entry: `|` User not registered in our database.");
        } else {
            let update = `UPDATE usuarios SET warns=0 WHERE idusuario = ${id}`;

            db.run(update, function(err) {
                if (err) return console.error(err.message)
            });

            const admin = message.author;
            const embed = new Discord.RichEmbed()
                .setAuthor("User Unwarned", client.user.avatarURL)
                .addField("Moderator: ", admin)
                .addField("User Unwarned: ", user)
                .addField("Reason: ", razon)
                .setColor(0x0E83A)
                .setTimestamp()
                    
            message.channel.send({embed});
            user.send({embed});
        }
    });

    }
    if (message.content.startsWith(prefix + "log")) {
        var perms = message.member.hasPermission("ADMINISTRATOR");
        if(!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You don't have ADMINISTRATOR permssion.");
    
        let SQL = "CREATE TABLE IF NOT EXISTS log (idguild TEXT, channelid TEXT)";

        db.run(SQL, function(err) {
            if (err) return console.error(err.message)
        });

        var id = message.guild.id
        //start search if the channel was configurated before
        let sentencia = `SELECT * FROM log WHERE idguild = ${id}`;

        const args = message.content.slice(prefix.length).trim().split(/ +/g);
        var razon = args.slice(1).join(' ');
        if(razon) {
            //there're args
            let channel = message.mentions.channels.first();
            let chnlid = channel.id

            db.get(sentencia, (err, filas) => {
                    if (err) return console.error(err.message)
                    if (!filas){
                        let SQL = "CREATE TABLE IF NOT EXISTS log (idguild TEXT, channelid TEXT)";

                        db.run(SQL, function(err) {
                            if (err) return console.error(err.message)
                        });
                        //non configurated never?
                         let insert = `INSERT INTO log(idguild, channelid) VALUES(${id}, ${chnlid})`;

                          db.run(insert, function(err) {
                           if (err) return console.error(err.message)
                          });

                          message.channel.send("Operation Success!");

                    } else {
                        let SQL = "CREATE TABLE IF NOT EXISTS log (idguild TEXT, channelid TEXT)";

                        db.run(SQL, function(err) {
                            if (err) return console.error(err.message)
                        });
                        //editing log channel? -> UPDATE
                         let update = `UPDATE log SET channelid = ${chnlid} WHERE idguild = ${id}`;
                          db.run(update, function(err) {
                            if (err) return console.error(err.message)
                        });
                        message.channel.send("Operation Success!");
                    }
                });

        } else { 
            let SQL = "CREATE TABLE IF NOT EXISTS log (idguild TEXT, channelid TEXT)";

            db.run(SQL, function(err) {
                if (err) return console.error(err.message)
            });
            //NO ARGS
            var id = message.guild.id
            let actchnlog = `SELECT * FROM log WHERE idguild = ${id}`;
            db.get(actchnlog, (err, filas) => {
                if (err) return console.error(err.message)
                if (filas){
                    let dbchnl = `${filas.channelid}`
                const embed =  new Discord.RichEmbed()
                    .setColor(0x0E83A)
                    .setAuthor(`Hammer Logging Channel`, client.user.avatarURL)
                    .setThumbnail(client.user.avatarURL)
                    .addField('**Actual Logging Channel**', `${dbchnl}`)
                    .addField("**How to configure it:**", "``/log #channel``")
                    .setTimestamp()
                    .setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
                    message.channel.send({embed});
                } else {
                    //never registered
                     const embed = new Discord.RichEmbed()
                    .setColor(0x0E83A)
                    .setAuthor(`Hammer Logging Channel`, client.user.avatarURL)
                    .setThumbnail(client.user.avatarURL)
                    .addField('**Actual Logging Channel**', "``None``")
                    .addField("**How to configure it:**", "``/log #channel``")
                    .setTimestamp()
                    .setFooter(`Comand executed by ${message.author.username}`, message.author.avatarURL)
                    message.channel.send({embed});
                }
            });
        }
        
        
        
    } 
    if (message.content.startsWith(prefix + "whois")) {
        let userm = message.mentions.users.first()

        if(!userm){
          var user = message.author;
               let usrid = user.id;
            let sentencia = `SELECT * FROM usuarios WHERE idusuario = ${usrid}`;
             db.get(sentencia, (err, filas) => {
            if (err) return console.error(err.message)

            if (filas){
            
            const embed = new Discord.RichEmbed()
            .setThumbnail(user.avatarURL)
            .setAuthor(user.username+'#'+user.discriminator, user.avatarURL)
            .addField('Playing', user.presence.game != null ? user.presence.game.name : "Nothing", true)
            .addField('ID', user.id, true)
            .addField('Status', user.presence.status, true)
            .addField('Nickname', message.member.nickname, true)
            .addField('Created Account', user.createdAt.toDateString(), true)
            .addField('Join Date', message.member.joinedAt.toDateString())
            .addField('Warns', `${filas.warns}`)
            .addField('Roles', message.member.roles.map(roles => `\`${roles.name}\``).join(', '))
            .setColor(0x66b3ff)
            message.channel.send(embed);
            } else {
                const embed = new Discord.RichEmbed()
            .setThumbnail(user.avatarURL)
            .setAuthor(user.username+'#'+user.discriminator, user.avatarURL)
            .addField('Playing', user.presence.game != null ? user.presence.game.name : "Nothing", true)
            .addField('ID', user.id, true)
            .addField('Status', user.presence.status, true)
            .addField('Nickname', message.member.nickname, true)
            .addField('Created Account', user.createdAt.toDateString(), true)
            .addField('Join Date', message.member.joinedAt.toDateString())
            .addField('Warns', `0`)
            .addField('Roles', message.member.roles.map(roles => `\`${roles.name}\``).join(', '))
            .setColor(0x66b3ff)
                
          message.channel.send(embed);
            }
            

        });
        
        } else {

            let id = userm.id;
            let sentencia = `SELECT * FROM usuarios WHERE idusuario = ${id}`;
             db.get(sentencia, (err, filas) => {
            if (err) return console.error(err.message)

            if (filas){
              const embed = new Discord.RichEmbed()
                .setThumbnail(userm.avatarURL)
                .setAuthor(userm.username+'#'+userm.discriminator, userm.avatarURL)
                .addField('Playing', userm.presence.game != null ? userm.presence.game.name : "Nothing", true)
                .addField('ID', userm.id, true)
                .addField('Status', userm.presence.status, true)
                .addField('Created Account', userm.createdAt.toDateString(), true)
                .addField('Warns', `${filas.warns}`)
                .setColor(0x66b3ff)
                message.channel.send(embed);
            } else {
                const embed = new Discord.RichEmbed()
                .setThumbnail(userm.avatarURL)
                .setAuthor(userm.username+'#'+userm.discriminator, userm.avatarURL)
                .addField('Playing', userm.presence.game != null ? userm.presence.game.name : "Nothing", true)
                .addField('ID', userm.id, true)
                .addField('Status', userm.presence.status, true)
                .addField('Created Account', userm.createdAt.toDateString(), true)
                .addField('Warns', `0`)
                .setColor(0x66b3ff)
                message.channel.send(embed);

            }
            
          
      });
        }
    }
    if (message.content.startsWith(prefix + "report")) {
        var id = message.guild.id
    //start search if the channel was configurated before
    let join = `SELECT * FROM log WHERE idguild = ${id}`;
    db.get(join, (err, filas) => {
       if (err) return console.error(err.message)
        if (filas){
         let channel = client.channels.get(`${filas.channelid}`); 
         let user = message.author;
         const args = message.content.split(" ").slice(1);
         let reporte = args.join(' ');
         if(!reporte) return message.channel.send(`:grey_exclamation: | **Send a report or questions to server STAFF**`)
         
         const embed = new Discord.RichEmbed()
          .setTitle(':e_mail: | **Report**')
          .setDescription('`Your report has been sent to server administators.`')
          .setDescription(reporte)
          .setThumbnail(`https://media.discordapp.net/attachments/576980879226961935/577344574931075072/carta.gif`)
          .setColor(0x77AEFF)
          .setFooter(`Report sent by ${message.author.username}#${message.author.discriminator}`, message.author.avatarURL)

         channel.send(embed)
         message.channel.send(":white_check_mark: | **Report Sent**").then(m =>  m.react("\u2709"))
                
         
    } else {message.channel.send("No log channel set. Use /log to configure it.");}

    });
    }
    if (message.content.startsWith(prefix + "lock")) {
        var perms = message.member.hasPermission('MANAGE_MESSAGES');
        if (!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You haven't the MANAGE_MESSAGES permission.");
         message.delete(100);
         message.channel.overwritePermissions(message.guild.id, {
         SEND_MESSAGES: false

           }).then(() => {
               message.channel.send(`:lock: This channel was **locked** by ${message.author.username}#${message.author.discriminator}`);
           });
    }
    if (message.content.startsWith(prefix + "unlock")) {
        var perms = message.member.hasPermission("ADMINISTRATOR");
        if (!perms) return message.channel.send(":no_entry: `Error` :no_entry: `|` You haven't the MANAGE_MESSAGES permission.");
         message.delete(100);
         message.channel.overwritePermissions(message.guild.id, {
         SEND_MESSAGES: true

           }).then(() => {
               message.channel.send(`:unlock: This channel was **unlocked** by ${message.author.username}#${message.author.discriminator}`);
           });
    }
    if (message.content.startsWith(prefix + "roles")) {
        let id = message.guild.id;
        const embed = new Discord.RichEmbed()
         .setAuthor('Roles of: '+ message.guild.name)
         .setThumbnail(message.guild.iconURL)
         .setColor(0x00AE86)
         .setDescription(`${client.guilds.get(id).roles.map(r => r.name).join(", ")}`)
        
        
    message.channel.send(embed);
    }

    if (message.content.startsWith(prefix + "guild")) {
    var server = message.guild;
    let id = message.guild.id;
    const embed = new Discord.RichEmbed()
    .setThumbnail(server.iconURL)
    .setAuthor(server.name, server.iconURL)
    .addField('ID', server.id, true)
    .addField('Region', server.region, true)
    .addField('Created', server.joinedAt.toDateString(), true)
    .addField('Guild Owner', server.owner.user.tag+' ('+server.owner.user.id +')', true)
    .addField('Members', server.memberCount, true)
    .addField('Roles', client.guilds.get(id).roles.map(r => r.name).join(", "), true)
    .setColor(0x66b3ff)
        
    message.channel.send(embed);
    }
    
        

});
client.login(process.env.TOKEN);
