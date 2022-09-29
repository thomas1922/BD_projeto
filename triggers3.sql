create or replace function triger3()
returns trigger
language plpgsql
as $$
    
begin
    insert into notificacoes(mensagem, utilizador_id)
    values('O utilizador de id' || new.coment_utilizador_id || 
           ' respondeu ao seu comentario', new.coment_utilizador_id1);
    
return null;
end;
$$;

create or replace trigger notifica after insert on coment_coment for each row
execute function triger3()