
create or replace function triger1()
returns trigger
language plpgsql
as $$
declare
    iduser integer;
    
begin
    select vendedor_utilizador_id into iduser from produto
    where produtoid=new.produto_produtoid and versao=new.produto_versao;
    
    insert into notificacoes(mensagem, utilizador_id)
    values('Foi feito um comentário sobre o produto de id ' || new.produto_produtoid, iduser);
    
return null;
end;
$$;


create or replace trigger notifica after insert on coment for each row
execute function triger1()
